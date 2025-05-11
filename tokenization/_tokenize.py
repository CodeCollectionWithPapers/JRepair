import re


COMPOSED_SYMBOLS = ['<<', '>>', '==', '!=', '>=', '<=', '&&', '||', '++', '--', '-=', '+=', '*=', '/=', '%=', '&=',
                    '|=', '^=', '<<=', '>>=', '->', '<-', '::']
def JRepair_tokenize(string):
    final_token_list = []
    string_replaced = extract_strings(string)
    split_tokens = re.split(r'([\W_])', string_replaced)
    split_tokens = list(filter(lambda a: a not in [' ', '', '"', "'", '\t', '\n'], split_tokens))
    flag = False

    # identifier seeting
    for idx, token in enumerate(split_tokens):
        if idx < len(split_tokens) - 1:
            reconstructed_token = token + split_tokens[idx + 1]
            if reconstructed_token in COMPOSED_SYMBOLS:
                final_token_list.append(reconstructed_token)
                flag = True
            elif not flag:
                final_token_list.append(token)
            elif flag:
                flag = False
        else:
            final_token_list.append(token)
    # camel seeting
    no_camel = []
    for token in final_token_list:
        camel_tokens = camel_case_split(token)
        for idx, camel_tok in enumerate(camel_tokens):
            no_camel.append(camel_tok)

    # string split seeting
    tokens = []
    for token in no_camel:
        number_sep = number_split(token)
        for num in number_sep:
            tokens.append(num)
    tokens = remove_integer(tokens)
    for idx, token in enumerate(tokens):
        if token == 'SSSTRINGSS':
            if idx > 0 and tokens[idx - 1] == '$STRING$':
                return []
            else:
                tokens[idx] = '$STRING$'

    return tokens

######################################-functions preparing-######################################
def extract_strings(string):

    matches = re.sub(r'"([^"]*)"', " SSSTRINGSS ", string)
    matches = re.sub(r"'([^']*)'", " SSSTRINGSS ", matches)
    return matches

def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    cam_toks = [m.group(0) for m in matches]
    results = []
    for tok in cam_toks:
        results.append(tok)
        results.append('CaMeL')
    if results:
        results.pop()
    return results

def number_split(identifier):
    match = re.findall('\d+|\D+', identifier)
    return match

def remove_integer(tokens):
    for idx, tok in enumerate(tokens):
        if tok.isdigit():
            try:
                if int(tok) > 1:
                    if int(tok) != 8 and int(tok) != 16 and int(tok) != 32 and int(tok) != 64:
                        tokens[idx] = '$NUMBER$'
            except:
                tokens[idx] = tok
    return tokens