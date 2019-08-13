def compress_numeric_string(data):
    output = b''
    idx = 0
    while idx<len(data):
        if idx%64 == 0:
            output+=bytes([(((min(64,len(data[idx:]))+1)//2-1)<<3) | 1])
        q = b'0123456789.,:; '.index(data[idx])<<4
        if len(data)>idx+1:
            q |=b'0123456789.,:; '.index(data[idx+1])
        else:
            q |= 0xF
        idx+=2
        output+=bytes([q])
    return output
def compress_bin(data):
    output = b''
    idx = 0
    while idx<len(data):
        output+=bytes([(min(32,len(data[idx:]))-1)<<3])
        output+=bytes(data[idx:idx+32])
        idx+=32
    return output
string_decoding=[]
for i in range(0x41, 0x5B):
    string_decoding.append(bytes([i]))
string_decoding+=[b' ',b"'", b',', b':', b';', b'.']
for i in range(0x61, 0x7B):
    string_decoding.append(bytes([i]))
string_decoding+=[
    b'=',
    b'\n',
    b'\r',
    b'#',
    b'_',
    b''
    ]
string_coding={}
for i in range(len(string_decoding)):
    q = string_decoding[i]
    if len(q)==1:
        q=q[0]
    string_coding[q]=i
def _get_string_symbol(data, idx):
    """for i in [b'OK',b'YES',b'NO',b'ERROR',b'rror']:
        if data[idx:].startswith(i):
            return i, idx+len(i)"""
    return data[idx], idx+1
def compress_string(data):
    output = b''
    idx = 0
    tmp_out = b''
    try:
        while idx<len(data):
            if len(tmp_out)==30:
                output+=bytes([((len(tmp_out)-1)<<3)|2])+tmp_out
                tmp_out = b''
            raw_text, idx = _get_string_symbol(data, idx)
            val = string_coding[raw_text]
            t1 = b''
            if idx<len(data):
                raw_text, idx = _get_string_symbol(data, idx)
                nx = string_coding[raw_text]
                val|=(nx&3)<<6
                val2 = nx>>2
                if idx<len(data):
                    raw_text, idx = _get_string_symbol(data, idx)
                    nx = string_coding[raw_text]
                    val2|=(nx&15)<<4
                    val3 = nx>>4
                    if idx<len(data):
                        raw_text, idx = _get_string_symbol(data, idx)
                        nx = string_coding[raw_text]
                        val3|=nx<<2
                    else:
                        val3|=0xFC
                    tmp_out+=bytes([val,val2,val3])
                else:
                    tmp_out+=bytes([val,val2])
            else:
                tmp_out+=bytes([val])
        if len(tmp_out)>0:
            output+=bytes([((len(tmp_out)-1)<<3)|2])+tmp_out
    except Exception as e:
        print("idx = "+str(idx))
        print("data = "+repr(data))
        print("tmp_out = "+repr(tmp_out))
        raise e
    return output
def compress_cts1(data):
    if type(data)==str:
        data = data.encode()

    output = b''
    
    TYPE_NONE = 0
    TYPE_STRING = 1
    TYPE_NUMERIC = 2
    TYPE_BINARY = 3
    tmp = b''
    tmp_type = TYPE_NONE
    for i in data:
        if tmp_type!=TYPE_NONE:
            if tmp_type==TYPE_STRING and not i in string_coding.keys():
                if len(tmp)<3:
                    tmp_type = TYPE_BINARY
                else:
                    output+=compress_string(tmp)
                    tmp = b''
                    if i in b'0123456789.,:; ':
                        tmp_type = TYPE_NUMERIC
                    else:
                        tmp_type = TYPE_BINARY
            elif tmp_type==TYPE_NUMERIC and not i in b'0123456789.,:; ':
                if len(tmp)<2:
                    tmp_type = TYPE_BINARY
                else:
                    output+=compress_numeric_string(tmp)
                    tmp = b''
                    if i in string_coding.keys():
                        tmp_type = TYPE_STRING
                    else:
                        tmp_type = TYPE_BINARY
            elif tmp_type==TYPE_BINARY and len(tmp)>0:
                if i in b'0123456789.,:; ':
                    output+=compress_bin(tmp)
                    tmp = b''
                    tmp_type = TYPE_NUMERIC
                elif i in string_coding.keys():
                    output+=compress_bin(tmp)
                    tmp = b''
                    tmp_type = TYPE_STRING
                
        else:
            if i in b'0123456789.,:; ':
                tmp_type = TYPE_NUMERIC
            elif i in string_coding.keys():
                tmp_type = TYPE_STRING
            else:
                tmp_type = TYPE_BINARY
        tmp+=bytes([i])
    if tmp_type==TYPE_NUMERIC:
        output+=compress_numeric_string(tmp)
    elif tmp_type==TYPE_STRING:
        output+=compress_string(tmp)
    elif tmp_type==TYPE_BINARY:
        output+=compress_bin(tmp)
    return output
def decompress_cts1(raw):
    output = b''
    idx = 0
    while idx<len(raw):
        cfg = raw[idx]
        idx+=1
        length = (cfg>>3) + 1
        coding = cfg&7
        if coding==0:
            output+=raw[idx:idx+length]
            idx+=length
        elif coding==1:
            unpackable = raw[idx:idx+length]
            for i in unpackable:
                a = i>>4
                b = i&15
                if a!=15:
                    output+=bytes([b'0123456789.,:; '[a]])
                if b!=15:
                    output+=bytes([b'0123456789.,:; '[b]])
            idx+=length
        elif coding==2:
            unpackable = raw[idx:idx+length]
            i = 0
            while i<len(unpackable):
                val = unpackable[i]
                c1 = string_decoding[val&63]
                i+=1
                if i<len(unpackable):
                    val2 = unpackable[i]
                    c2 = string_decoding[((15&val2)<<2)|(val>>6)]
                    i+=1
                    if i<len(unpackable):
                        val3 = unpackable[i]
                        c3 = ((val3&3)<<4)|(val2>>4)
                        c3 = string_decoding[c3]
                        c4 = string_decoding[(val3>>2)]
                        output+=c1+c2+c3+c4
                        i+=1
                    else:
                        output+=c1+c2
                else:
                    output+=c1
            idx+=length
    return output
def get_compression_ratio(original):
    return len(compress_cts1(original))/len(original)
