import os
import sys
import tarfile

nbpe = 5000
bpemode = "unigram"
fairseq_root = "/home/user/install/fairseq"

DATA_FOLDER = "/home/user/data/"

if __name__ == "__main__":
    PATH_TO_RAW_DATA = os.path.join(DATA_FOLDER, "raw_data/")
    PATH_TO_PREP_DATA = os.path.join(DATA_FOLDER, "prep_data/")

    for dirname in os.listdir(PATH_TO_RAW_DATA):
        tar = tarfile.open(os.path.join(PATH_TO_RAW_DATA, dirname), "r:gz")
        tar.extractall(path=PATH_TO_PREP_DATA)
        tar.close()


    train_dir = os.path.join(PATH_TO_PREP_DATA, "train_dir")
    audio_dir = os.path.join(train_dir, "audio")
    val_dir = os.path.join(PATH_TO_PREP_DATA, "val_dir")
    lang_char_dir = os.path.join(PATH_TO_PREP_DATA, "lang_char")

    train_transcriptions_file = os.path.join(train_dir, "text")

    os.mkdir(train_dir)
    os.mkdir(val_dir)
    os.mkdir(lang_char_dir)
    os.mkdir(audio_dir)


    filename_to_index = {}

    group_subgr = "8842-304647"
    last_index = 10000

    texts = []
    for dataset in os.listdir(PATH_TO_PREP_DATA):
        dataset_path = os.path.join(PATH_TO_PREP_DATA, dataset)
        if (dataset == "train_dir" or dataset == "val_dir" or dataset == "text" or dataset == "lang_char"):
            continue 
        print("DATASET: ", dataset)
        for group in os.listdir(dataset_path):
            group_path = os.path.join(dataset_path, group)
            print("*", end='')
            for subgroup in os.listdir(group_path):
                subgroup_path = os.path.join(group_path, subgroup)
                for f in os.listdir(subgroup_path):
                    file_path = os.path.join(subgroup_path, f)
                    if f.endswith(".txt"):
                        filename = f[:-4]
                        transcription = open(file_path).read()
                        texts.append(transcription)

                        if filename not in filename_to_index:
                            filename_to_index[filename] = last_index
                            open(train_transcriptions_file, "a+").write(f"{group_subgr}-{last_index} {transcription.upper()}")
                            last_index += 1
                        else:
                            open(train_transcriptions_file, "a+").write(f"{group_subgr}-{filename_to_index[filename]} {transcription}")
                    else:
                        if f.endswith(".opus"):
                            filename = f[:-5]

                            flac_path = None
                            if filename not in filename_to_index:
                                filename_to_index[filename] = last_index
                                flac_path = os.path.join(audio_dir, f"{group_subgr}-{last_index}.flac")
                                last_index += 1
                            else:
                                flac_path = os.path.join(audio_dir, f"{group_subgr}-{filename_to_index[filename]}.flac")
                            os.system(f'ffmpeg -i {file_path} {flac_path} -loglevel quiet')
                print("+", end='')
            
        print()


    dict_file = os.path.join(lang_char_dir, f"train_dir_{bpemode}{nbpe}_units.txt")
    encoded_file = os.path.join(lang_char_dir, f"train_dir_{bpemode}{nbpe}_encoded.txt")
    fairseq_dict_file = os.path.join(lang_char_dir, f"train_dir_{bpemode}{nbpe}_fairseq_dict.txt")
    bpemodel_file = os.path.join(lang_char_dir, f"train_dir_{bpemode}{nbpe}")

    os.mknod(dict_file)
    os.mknod(encoded_file)
    os.mknod(fairseq_dict_file)
    os.mknod(bpemodel_file)

    os.system(f'echo "<unk> 3" > {dict_file}')
    os.system(f'echo "</s> 2" >> {dict_file}')
    os.system(f'echo "<pad> 1" >> {dict_file}')

    input_file = os.path.join(lang_char_dir, "input.txt")
    open(input_file, "w").write("\n".join(texts))
    os.system(f"spm_train --input={input_file} --vocab_size={nbpe} --model_type={bpemode} --model_prefix={bpemodel_file} --input_sentence_size=100000000 --unk_id=3 --eos_id=2 --pad_id=1 --bos_id=-1 --character_coverage=1")
    os.system(f"spm_encode --model={bpemodel_file}.model --output_format=piece < {input_file} > {encoded_file}")
    
    os.system(f"cat {encoded_file} | tr ' ' '\n' | sort | uniq | awk '" + '{print $0 " " NR+3}' + "'" + f" >> {dict_file}")
    os.system(f"cat {encoded_file} | tr ' ' '\n' | sort | uniq -c | awk '" + '{print $2 " " $1}' + "' > " + f"{fairseq_dict_file}")
    os.system(f"wc -l {dict_file}")

    os.system(f"python {fairseq_root}/examples/speech_recognition/datasets/asr_prep_json.py --audio-dirs {audio_dir} --labels {train_transcriptions_file} --spm-model {bpemodel_file}.model --audio-format flac --dictionary {fairseq_dict_file} --output {os.path.join(DATA_FOLDER, 'train.json')}")

    os.system(f"cp {fairseq_dict_file} {os.path.join(DATA_FOLDER, 'dict.txt')}")
    os.system(f"cp {bpemodel_file}.model {os.path.join(DATA_FOLDER, 'spm.model')}")