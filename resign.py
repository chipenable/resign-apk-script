#! /usr/bin/env python

import os
import sys
import shutil
import json
import argparse
import re
import zipfile

def zipalign_path(): 

    return os.path.join(get_script_dir(), 'tools', 'zipalign')

def apksigner_path():

    return os.path.join(get_script_dir(), 'tools', 'apksigner.jar')

def keystores_json_path():

    return os.path.join(get_script_dir(), 'keystores.json')

def get_script_dir():

    script_path = os.path.realpath(__file__)
    (script_dir, _) = os.path.split(script_path)
    return script_dir   

def get_keystores():
    '''return available keystores'''

    keystores_json = keystores_json_path()

    if not os.path.exists(keystores_json):
        raise Exception('can not find keystores.json')

    keystores = []

    with open(keystores_json) as in_file:
        json_data = json.load(in_file)
        for keystore in json_data:
            keystores.append(keystore)

    return keystores    

def sign_apk(**kwargs):

    apk_file = kwargs['input_file']
    output_file = kwargs['output_file']
    keystore = os.path.join(get_script_dir(), kwargs['keystore'])
    password = kwargs['password']
    alias = kwargs['alias']
    alias_password = kwargs['alias_password']
    apksigner = apksigner_path()

    sign_com = 'java -jar {0} sign --ks {1} --ks-key-alias {2} --ks-pass pass:{3} --key-pass pass:{4} --in {5} --out {6}'\
         .format(apksigner, keystore, alias, password, alias_password, apk_file, output_file)
    result = os.system(sign_com)

    apk_file_name = os.path.basename(output_file)
    report = 'done' if result == 0 else 'fail'
    print 'Re-sign {0}: {1}'.format(apk_file_name, report)

    apksigner = apksigner_path()
    verify_com = 'java -jar {0} verify {1}'.format(apksigner, output_file)
    result = os.system(verify_com)

    apk_file_name = os.path.basename(output_file)
    report = 'done' if result == 0 else 'fail'
    print 'Verify {0}: {1}'.format(apk_file_name, report)

def re_sign(**kwargs):
    ''' re-sign apk file '''

    keystore = kwargs['keystore']
    apk_file = kwargs['apk_file']

    apk_file_name = apk_file.replace('.apk', '')
    temp_dir = 'temp'

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)

    ''' unzip apk file '''
    zip_ref = zipfile.ZipFile(apk_file)
    zip_ref.extractall(temp_dir)

    ''' delete previous signing info '''
    meta_inf_dir = os.path.join(temp_dir, 'META-INF')
    shutil.rmtree(meta_inf_dir, ignore_errors=True)

    shutil.make_archive(apk_file_name, 'zip', temp_dir)

    ''' rename to apk '''
    temp_zip_file = apk_file_name + '.zip'
    temp_apk_file = apk_file_name + '_unsigned.apk'
    os.rename(temp_zip_file, temp_apk_file)

    ''' align apk file '''
    aligned_apk_file = apk_file_name + '_aligned_unsigned.apk'
    zipalign = zipalign_path()
    com = '{0} -f 4 {1} {2}'.format(zipalign, temp_apk_file, aligned_apk_file)
    os.system(com) 

    keystores_json = keystores_json_path()
    with open(keystores_json) as in_file:
        json_data = json.load(in_file)

        keystore_file = json_data[keystore]['path']
        apk_suffix = '-' + keystore

        output_file = apk_file_name + apk_suffix + '.apk'
        output_full_path = os.path.join(output_file)

        sign_apk(
            input_file=aligned_apk_file, 
            output_file=output_full_path,
            keystore=json_data[keystore]['path'],
            password=json_data[keystore]['keystore_password'],
            alias=json_data[keystore]['alias'],
            alias_password=json_data[keystore]['alias_password']
        )

    ''' delete tmp files '''
    os.remove(temp_apk_file)
    os.remove(aligned_apk_file)
    shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    '''main function'''

    keystores = get_keystores()
    if not keystores: 
        print('you have no keystores')
        return

    parser = argparse.ArgumentParser(description='script to re-sign android applications')

    parser.add_argument(
        'keystore',
        nargs=1,
        choices=keystores,
        help='keystore for signing')

    parser.add_argument(
        'apk_file',
        nargs=1,
        help='android application that you want to re-sign')

    args = vars(parser.parse_args())

    if "help" in args:
        print parser.format_help()
        return

    re_sign(
        keystore=args['keystore'][0], 
        apk_file=args['apk_file'][0]
    )

if __name__ == "__main__":
    main()