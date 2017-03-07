#!/bin/bash

# Generated by ansible

cd {{ backup_folder_path }}
now=$(date +"%m-%d-%Y")
export AWS_SECRET_ACCESS_KEY="{{ AWS_SECRET_ACCESS_KEY }}"
export AWS_DEFAULT_REGION="{{ AWS_DEFAULT_REGION }}"
export AWS_ACCESS_KEY_ID="{{ AWS_ACCESS_KEY_ID }}"
export BACKUP_FILE="{{ backup_folder_path }}/log-files-$now-backup.aes"
export TEMPTAR_FILE="{{ backup_folder_path }}/log-files-$now-backup.tar.bz2"

sudo tar cjvf $TEMPTAR_FILE /var/log/{{ application_name }}/*
sudo openssl aes-256-cbc -a -salt -in $TEMPTAR_FILE -out $BACKUP_FILE -pass file:{{ encryption_key_path }}
aws s3 cp $BACKUP_FILE s3://{{ s3_backup_bucket_name }}/logs/$now.log.aes256 && rm $TEMPTAR_FILE
