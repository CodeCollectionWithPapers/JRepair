import argparse
import os

import yaml
import subprocess

import time



def JRepair_inference(config_file,clearml):
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
        f.close()
    use_clearml=config_dict['clearml']
    datadir=config_dict['datadir']
    modelpath=config_dict['modelpath']
    beam=config_dict['beam']
    nbest=config_dict['nbest']
    source=config_dict['source']
    target=config_dict['target']
    taskname=config_dict['taskname']
    outputfile=config_dict['outputfile']

    cmd ="python "+"JRepair_inference/generate.py "+datadir+" --path "+modelpath+" --beam "+str(beam)+" --nbest "+str(nbest)+\
        " -s "+source+" -t "+target+" -clearml "+str(use_clearml)+" -taskname "+taskname+" -outputfile "+outputfile+" --max-sentences 1"
    subprocess.call(cmd, shell=False)
    # os.system(cmd)
def main():
    parser = argparse.ArgumentParser(
        description='J_generate.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-config",default="JRepair_master/JRepair_config/JRepair_inference.yaml",help="location of config file",required=False)

    opt=parser.parse_args()
    start=time.time()

    JRepair_inference(config_file=opt.config,clearml=opt.clearml)
    end=time.time()
    time_sum=end-start
    print("total_time",time_sum)
if __name__ == "__main__":
    main()