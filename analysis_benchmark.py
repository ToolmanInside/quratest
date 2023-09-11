import os
import sys
import re
from logzero import logger
import math
import csv

sample_count = 100000
folder_prefix = "exp-02-"
generators = ["qft", "random", "ucnot"]
# generators = ['ucnot']
algorithms = ["adder", "bv", "dpc_pe", "dpc_qft", "grover", "pe", "qft", "rand_cliff"]
# algorithms = ['rand_cliff']

def extract_numbers(strs):
    return int(re.findall('\d+', strs)[0])

def shrink_list(file_list):
    result_list = [x for x in file_list if "result" in x]
    return_dict = dict()
    for algo in algorithms:
        tmp_list = [x for x in result_list if algo in x]
        tmp_list = sorted(tmp_list, key=extract_numbers)
        return_dict[algo] = str(extract_numbers(tmp_list[0])).zfill(2)
    return return_dict

def get_min_bits_dict(tmp_folder_path):
    file_list = os.listdir(tmp_folder_path)
    min_bits_dict = shrink_list(file_list)
    return min_bits_dict

def gen_bin_dict(num_qubits):
    output_list = list()
    output_list.append("0" * num_qubits)
    for i in range(1, pow(2, num_qubits)):
        tmp = list()
        r = 0
        while (i!=0):
            r = i%2
            i = i//2
            tmp = [str(r)] + tmp
        output_list.append("".join(tmp).zfill(num_qubits))
    output_dict = dict()
    for k in output_list:
        output_dict[k] = 0
    return output_dict

def coverage(distribution, num_qubits, plus_bit = False):
    # total_state_num = 2**len(list(distribution.keys())[0])
    if plus_bit == True:
        total_state_num = 2**(num_qubits + 1)
    else:
        total_state_num = 2**num_qubits
    cover_count = 0
    threshold = sample_count * 0.001
    threshold = 0
    for key, item in distribution.items():
        if item > threshold:
            cover_count += 1
    rate = round(cover_count/total_state_num, 2)
    return rate

def analysis(file_path, min_bits = 0):
    truncation_measure = False
    plus_bit = False
    num_qubits = int(extract_numbers(file_path.strip().split('/')[2]))
    algo = file_path.strip().split('/')[2]
    if 'pe' in algo:
        plus_bit = True
    if min_bits == 0:
        truncation_measure = False
    content = eval(open(file_path).read())
    if truncation_measure == True:
        tmp_bin_dict = gen_bin_dict(int(min_bits))
        for key, item in content.items():
            truncation = key[-int(min_bits):]
            tmp_bin_dict[truncation] += int(item)
        rate = coverage(tmp_bin_dict, num_qubits, plus_bit)
    elif truncation_measure == False:
        rate = coverage(content, num_qubits, plus_bit)
    return rate

def main(idx):
    return_list = list()
    folder_name = folder_prefix + idx
    tmp_folder_path = os.path.join(folder_name, "random")
    min_bits_dict = get_min_bits_dict(tmp_folder_path)
    # print(min_bits_dict)
    for gen in generators:
        folder_path = os.path.join(folder_name, gen)
        ff_list = os.listdir(folder_path)
        for ff in ff_list:
            if "circuit" in ff:
                continue
            splits = ff.strip().split('_')
            if len(splits) == 4:
                algo = splits[1]
                bits = splits[2]
            elif len(splits) == 5:
                algo = splits[1] + '_' + splits[2]
                bits = splits[3]
            min_bits = min_bits_dict[algo]
            if bits == min_bits:
                rate = analysis(os.path.join(folder_path, ff))
            else:
                rate = analysis(os.path.join(folder_path, ff), min_bits)
            # logger.debug("Generator {0} has {1} coverage rate on {2} algorithm".format(gen, str(rate), algo))
            # print("{} {} {} {}".format(gen, str(rate), algo, bits))
            return_list.append((gen, str(rate), algo, bits))
    # print("============== New Index ==============")
    return return_list

if __name__ == "__main__":
    run_time = 100
    data_sum = dict()
    for i in range(run_time):
        idx = str(i).zfill(2)
        return_list = main(idx)
        for rr in return_list:
            generator, rate, algo, bits = rr
            k = generator + "_" + algo + "_" + bits
            if k not in data_sum.keys():
                data_sum[k] = 0.0
            data_sum[k] += round(float(rate), 2)
    for gg in generators:
        with open(gg+'.csv', 'w') as ff:
            writer = csv.writer(ff)
            writer.writerow(['U', "Algo", "Qubits", "Coverage"])
            writing_list = list()
            for i, t in data_sum.items():
                splits = i.strip().split('_')
                if len(splits) == 3:
                    gen = splits[0]
                    algo = splits[1]
                    bits = splits[2]
                elif len(splits) == 4:
                    gen = splits[0]
                    algo = splits[1] + '_' + splits[2]
                    bits = splits[3]
                if gen != gg:
                    continue
                writing_list.append((gen, algo, bits, t))
            writing_list.sort(key = lambda x: (x[1], x[2]))
            for ww in writing_list:
                writer.writerow([ww[0], ww[1], ww[2], ww[3]])