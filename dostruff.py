import os
import shutil
import subprocess

def read_map_file(map_file):
    with open(map_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    filename = lines[0]
    directory = lines[1]
    ids = lines[2:]
    return filename, directory, ids

def get_audio_sets(input_folder, ids):
    sets = {}
    max_files = 0
    id_files = {}
    
    for root, dirs, files in os.walk(input_folder):
        for id_ in ids:
            folder_path = os.path.join(root, id_)
            if os.path.exists(folder_path):
                audio_files = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".wav") or f.endswith(".wem")])
                if audio_files:
                    id_files[id_] = audio_files
                    max_files = max(max_files, len(audio_files))
    
    for i in range(max_files):
        set_files = []
        for id_, files in id_files.items():
            if i < len(files):
                set_files.append((id_, files[i]))
        sets[i] = set_files
    
    return sets

def update_conversion_map(conversion_map_path, set_files):
    with open(conversion_map_path, 'w', encoding='utf-8') as f:
        for id_, file in set_files:
            f.write(f"{id_} {id_}.wem\n")

def clear_audio_files(audio_dir):
    for file in os.listdir(audio_dir):
        file_path = os.path.join(audio_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

def copy_and_rename_files(set_files, audio_dir):
    for id_, file in set_files:
        dest_file = os.path.join(audio_dir, f"{id_}.wav")
        shutil.copy(file, dest_file)

def run_conversion(audio_dir):
    files = [os.path.abspath(os.path.join(audio_dir, f)) for f in os.listdir(audio_dir) if f.endswith(".wav")]
    if files:
        files = [f'"{file.replace("/", "\\")}"' for file in files]  # Ensure backslashes and proper quoting
        command = f'wavwem\\zSound2wem.cmd {" ".join(files)}'
        subprocess.run(command, shell=True, check=True)



def move_wem_files(wem_dir, audio_dir):
    for file in os.listdir(wem_dir):
        if file.endswith(".wem"):
            shutil.move(os.path.join(wem_dir, file), os.path.join(audio_dir, file))

def run_repacker(filename, set_number):
    output_wpk = f"set-{set_number}.wpk"
    print(filename)
    subprocess.run(["converter\\NMSBnkRepacker.exe", f"converter\\{filename}", output_wpk], shell=True)
    return output_wpk

def copy_wpk_to_output(output_wpk, directory, filename):
    # Ensure the directory uses forward slashes
    output_path = os.path.join(directory.replace("\\", "/"), filename)

    # Check if the directory exists; if not, create it
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # If the file exists, remove it to overwrite
    if os.path.exists(output_path):
        os.remove(output_path)

    # Move the WPK file to the output directory, overwriting if needed
    shutil.move(output_wpk, output_path)


def run_wad_make(directory):
    first_folder = os.path.abspath(directory.split("\\")[0])
    subprocess.run(["REPLACE WITH wad-make.exe path", first_folder], shell=True)
    return f"{first_folder}.wad.client"

def move_wad_file(wad_file, directory, set_number):
    first_folder = os.path.abspath(directory.split("\\")[0])
    dest_folder = f"{first_folder}-set-{set_number}/"
    counter = 2
    while os.path.exists(dest_folder):
        dest_folder = f"{first_folder}-set-{set_number}-{counter}/"
        counter += 1
    os.makedirs(dest_folder)
    shutil.move(wad_file, dest_folder)

def main():
    map_file = "input/map.txt"
    input_folder = "input"
    conversion_map_path = "ConversionMap.txt"
    audio_dir = "AudioFiles/"
    wem_dir = "wavwem/"
    
    filename, directory, ids = read_map_file(map_file)
    sets = get_audio_sets(input_folder, ids)
    
    for set_number, set_files in sets.items():
        update_conversion_map(conversion_map_path, set_files)
        clear_audio_files(audio_dir)
        copy_and_rename_files(set_files, audio_dir)
        run_conversion(audio_dir)
        move_wem_files(wem_dir, audio_dir)
        output_wpk = run_repacker(filename, set_number)
        copy_wpk_to_output(output_wpk, directory, filename)
        wad_file = run_wad_make(directory)
        move_wad_file(wad_file, directory, set_number)

if __name__ == "__main__":
    main()
