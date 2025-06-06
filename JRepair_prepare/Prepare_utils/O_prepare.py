import javalang
import json
import codecs
def writeL2F(contents:list,filepath):
    with open(filepath,'w',encoding='utf-8')as f:
        for idx,line in enumerate(contents):
            print(idx,line)
            f.write(str(line)+'\n')
        f.close()

def readJavaFile(filepath):
    tokens = list(javalang.tokenizer.tokenize('if(!working_dir.exists() || !working_dir.isDirectory()) {'))
    for tok in tokens:
        print(tok)

def writeD2J(contents:dict,filepath):
    jsonObj=json.dumps(contents,indent=4)
    with open(filepath,'w',encoding='utf8')as f:
        f.write(jsonObj)
        f.close()

def readF2L(filepath):
    lines=[]
    with open(filepath,'r',encoding='utf-8')as f:
        for line in f:
            lines.append(line.strip())
        f.close()
    return lines
def readF2L_ori(filepath):
    lines=[]
    with open(filepath,'r',encoding='utf-8')as f:
        for line in f:
            lines.append(line)
        f.close()
    return lines
def readF2L_enc(filepath,enc):
    lines=[]
    with open(filepath,'r',encoding=enc)as f:
        for line in f:
            lines.append(line.strip())
        f.close()
    return lines
def write2F(content:str,filepath):
    f=codecs.open(filepath,'w',encoding='utf8')
    f.write(content)
    f.close()

