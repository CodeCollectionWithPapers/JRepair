import codecs
import os
import re
import subprocess

from tqdm import tqdm
from JRepair_prepare.Prepare_utils.O_prepare import readF2L, writeL2F
from tokenization._tokenize import JRepair_tokenize


def Preprocess_JRepair_RawData(ids_f,input_dir,temp_prefix,output_dir,src_dict_f,tgt_dict_f,mode):
    ids=readF2L(ids_f)
    buggy_codes=[]
    repair_lines=[]
    id_flag = ''
    # for id in ids:
    for id in ids:
        buggy_line = codecs.open(input_dir+'/buggy_line/'+id_flag+id+'.txt','r','utf-8',errors='replace').read().strip()
        buggy_method = codecs.open(input_dir + '/buggy_method/' + id + '.txt','r','utf-8',errors='replace').read().strip()
        buggy_class = codecs.open(input_dir + '/buggy_class/' + id + '.txt','r','utf-8',errors='replace').read().strip()
        repair_line = codecs.open(input_dir+'/repair_line/'+id_flag+id+'.txt','r','utf-8',errors='replace').read().strip()
        repair_method = codecs.open(input_dir + '/repair_method/' + id_flag + id + '.txt', 'r', 'utf-8',errors='replace').read().strip()
        repair_class = codecs.open(input_dir + '/repair_class/' + id_flag + id + '.txt', 'r', 'utf-8',errors='replace').read().strip()

        # TODO tokenization for raw data
        buggy_method_toked = JRepair_tokenize(buggy_method)
        buggy_line_toked = JRepair_tokenize(buggy_line)
        fix_line_toked = JRepair_tokenize(repair_line)


        """context-free"""
        buggy_codes.append(' '.join(buggy_line_toked))
        """function-level"""
        # buggy_codes.append(' '.join(buggy_line_toked) + ' <CTX> ' + ' '.join(buggy_method_toked))
        """class-level"""
        # buggy_codes.append(' '.join(buggy_line_toked) + ' <CTX> ' + ' '.join(buggy_class_toked))

        repair_lines.append(' '.join(fix_line_toked))
    assert len(buggy_codes)==len(repair_lines)
    writeL2F(buggy_codes,temp_prefix+'.buggy')
    writeL2F(repair_lines,temp_prefix+'.fix')
    print("Start reprocessing source data...")

    if "test" in mode:
        cmd = "python JRepair_master/J_preprocess.py " + " --workers  2" \
          + " --srcdict " + src_dict_f + " --tgtdict " + tgt_dict_f + " --testpref " + temp_prefix + " --destdir " + output_dir
        print(cmd)
        subprocess.call(cmd, shell=False)


#Apply to source data
Preprocess_JRepair_RawData("Data_set/evaluation/test.ids","Data_set/evaluation",
                           "Processed/18_open_projects/raw_18_projects","Processed/18_open_projects/18_projects_eval",
                           "Processed/dict.ctx.txt","Processed/dict.fix.txt","18_pro_test")