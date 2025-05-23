#!/usr/bin/env python3 -u

"""
Generate JIT candidate patches.
"""
import codecs

import torch
import bleu,data, options, progress_bar, tasks, tokenizer, utils
from meters import StopwatchMeter, TimeMeter
from sequence_generator import SequenceGenerator
from sequence_scorer import SequenceScorer


def main(args):
    assert args.path is not None, '--path required for generation!'
    assert not args.sampling or args.nbest == args.beam, \
        '--sampling requires --nbest to be equal to --beam'
    assert args.replace_unk is None or args.raw_text, \
        '--replace-unk requires a raw text dataset (--raw-text)'

    if args.max_tokens is None and args.max_sentences is None:
        args.max_tokens = 12000

    output_f=codecs.open(args.outputfile,"w",encoding='utf8')

    use_cuda = torch.cuda.is_available() and not args.cpu

    torch.cuda.empty_cache()
    # Load dataset splits
    task = tasks.setup_task(args)
    task.load_dataset(args.gen_subset)   #gen_subset = test表示指定数据集

    print('| {} {} {} examples'.format(args.data, args.gen_subset, len(task.dataset(args.gen_subset))))

    # Set dictionaries
    src_dict = task.source_dictionary
    tgt_dict = task.target_dictionary

    # Load ensemble
    print('| loading model(s) from {}'.format(args.path))
    models, _ = utils.load_ensemble_for_inference(args.path.split(':'), task, model_arg_overrides=eval(args.model_overrides))

    for model in models:
        # print(next(model.parameters()).device)
        for name, module in model.named_modules():

        model.make_generation_fast_(
            beamable_mm_beam_size=None if args.no_beamable_mm else args.beam,
            need_attn=args.print_alignment,
        )
        if args.fp16:
            model.half()

    align_dict = utils.load_align_dict(args.replace_unk)

    max_positions = utils.resolve_max_positions(
        task.max_positions(),
        *[model.max_positions() for model in models]
    )
    # Load dataset (possibly sharded)
    itr = task.get_batch_iterator(
        dataset=task.dataset(args.gen_subset),
        max_tokens=args.max_tokens,
        max_sentences=args.max_sentences,
        max_positions=max_positions,
        # ignore_invalid_inputs=args.skip_invalid_size_inputs_valid_test,
        ignore_invalid_inputs=True,
        required_batch_size_multiple=8,
        num_shards=args.num_shards,
        shard_id=args.shard_id,
    ).next_epoch_itr(shuffle=False)
    # required_batch_size_multiple = 8


    # Initialize generator
    gen_timer = StopwatchMeter()

    if args.score_reference:
        translator = SequenceScorer(models, task.target_dictionary)
    else:
        translator = SequenceGenerator(
            models, task.target_dictionary, beam_size=args.beam, minlen=args.min_len,
            stop_early=(not args.no_early_stop), normalize_scores=(not args.unnormalized),
            len_penalty=args.lenpen, unk_penalty=args.unkpen,
            sampling=args.sampling, sampling_topk=args.sampling_topk, sampling_temperature=args.sampling_temperature,
            diverse_beam_groups=args.diverse_beam_groups, diverse_beam_strength=args.diverse_beam_strength,
        )

    if use_cuda:
        translator.cuda()

    # Generate and compute BLEU score

    scorer = bleu.Scorer(tgt_dict.pad(), tgt_dict.eos(), tgt_dict.unk())
    num_sentences = 0
    has_target = True

    translations_result=[]
    with progress_bar.build_progress_bar(args, itr) as t:
        if args.score_reference:
            translations = translator.score_batched_itr(t, cuda=use_cuda, timer=gen_timer)
        else:
            translations = translator.generate_batched_itr(
                t, maxlen_a=args.max_len_a, maxlen_b=args.max_len_b,
                cuda=use_cuda, timer=gen_timer, prefix_size=args.prefix_size,
            )


        wps_meter = TimeMeter()
        for sample_id, src_tokens, target_tokens, hypos in translations:

            has_target = target_tokens is not None
            target_tokens = target_tokens.int().cpu() if has_target else None


            # Either retrieve the original sentences or regenerate them from tokens.
            if align_dict is not None:
                src_str = task.dataset(args.gen_subset).src.get_original_text(sample_id)
                target_str = task.dataset(args.gen_subset).tgt.get_original_text(sample_id)
            else:
                src_str = src_dict.string(src_tokens, args.remove_bpe)
                if has_target:
                    target_str = tgt_dict.string(target_tokens, args.remove_bpe, escape_unk=True)
            if not args.quiet:
                print('S-{}\t{}'.format(sample_id, src_str),file=output_f)
                if has_target:
                    print('T-{}\t{}'.format(sample_id, target_str),file=output_f)

            for i, hypo in enumerate(hypos[:min(len(hypos), args.nbest)]):

                hypo_tokens, hypo_str, alignment = utils.post_process_prediction(
                    hypo_tokens=hypo['tokens'].int().cpu(),
                    src_str=src_str,
                    alignment=hypo['alignment'].int().cpu() if hypo['alignment'] is not None else None,
                    align_dict=align_dict,
                    tgt_dict=tgt_dict,
                    remove_bpe=args.remove_bpe,
                )
                if not args.quiet:
                    print('H-{}\t{}\t{}'.format(sample_id, hypo['score'], hypo_str),file=output_f)

                if has_target and i == 0:
                    if align_dict is not None or args.remove_bpe is not None:

                        target_tokens = tokenizer.Tokenizer.tokenize(
                            target_str, tgt_dict, add_if_not_exist=True)
                    scorer.add(target_tokens, hypo_tokens)

            wps_meter.update(src_tokens.size(0))
            t.log({'wps': round(wps_meter.avg)})
            num_sentences += 1

    print('| Translated {} sentences ({} tokens) in {:.1f}s ({:.2f} sentences/s, {:.2f} tokens/s)'.format(
        num_sentences, gen_timer.n, gen_timer.sum, num_sentences / gen_timer.sum, 1. / gen_timer.avg))
    if has_target:
        print('| Generate {} with beam={}: {}'.format(args.gen_subset, args.beam, scorer.result_string()))

        #print('| Generate {} with beam={}: {}'.format(args.gen_subset, args.beam))
def load_dicts(args):
    assert args.path is not None, '--path required for generation!'
    assert not args.sampling or args.nbest == args.beam, \
        '--sampling requires --nbest to be equal to --beam'
    assert args.replace_unk is None or args.raw_text, \
        '--replace-unk requires a raw text dataset (--raw-text)'

    if args.max_tokens is None and args.max_sentences is None:
        args.max_tokens = 12000

    output_f=codecs.open(args.outputfile,"w",encoding='utf8')
    print(args)

    use_cuda = torch.cuda.is_available() and not args.cpu

    task = tasks.setup_task(args)

    # Set dictionaries
    src_dict = task.source_dictionary
    tgt_dict = task.target_dictionary

    # Load ensemble
    print('| loading model(s) from {}'.format(args.path))
    models, _ = utils.load_ensemble_for_inference(args.path.split(':'), task, model_arg_overrides=eval(args.model_overrides))
    print(src_dict)
    print(tgt_dict)


if __name__ == '__main__':
    parser = options.get_generation_parser()
    parser.add_argument("-clearml",default=False,type=bool)
    parser.add_argument("-taskname",default='JIT_Repair')
    parser.add_argument("-outputfile",default='pred.txt')
    parser.add_argument("-device_id", default=0)
    parser.add_argument("--skip_invalid_size_inputs_valid_test", default=True)
    args = options.parse_args_and_arch(parser)
    print(args)
    main(args)
