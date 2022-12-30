#!/usr/bin/env bash
olddir=$(pwd)
outpath=$HOME/workspace/Apollo/lineage_data
cd $(dirname -- "${BASH_SOURCE[0]}")
python pull_training_data.py --path $outpath --site-id 62f3c57c4f236dfb2b2e854b --method existing_lineage
python pull_training_data.py --path $outpath --site-id 6331f59beb6b6bbfb6cadb9e --method link_text
python pull_training_data.py --path $outpath --site-id 62f3c5884f236dfb2b2e8a0d --method link_text_up_to --method-args="Effective,January"
python pull_training_data.py --path $outpath --site-id 637395404e44290ad8fe5de1 --method link_text_up_to --method-args="Effective"
python pull_training_data.py --path $outpath --site-id 62f3c5884f236dfb2b2e89e2 --method link_text_up_to --method-args="-"
python pull_training_data.py --path $outpath --site-id 62f3c5884f236dfb2b2e89f6 --method link_text
python pull_training_data.py --path $outpath --site-id 62f3c5834f236dfb2b2e883e --method existing_lineage
python pull_training_data.py --path $outpath --site-id 62f3c56f4f236dfb2b2e7fa0 --method existing_lineage
python pull_training_data.py --path $outpath --site-id 62f3c56f4f236dfb2b2e7fa0 --method link_text
python pull_training_data.py --path $outpath --site-id 6377e9250d3b10488dbd213f --method link_text
python pull_training_data.py --path $outpath --site-id 635c1b3e3b556884a36059eb --method link_text_up_to --method-args="Effective"
python pull_training_data.py --path $outpath --site-id 62f3c5824f236dfb2b2e87bb --method link_text
python pull_training_data.py --path $outpath --site-id 62f3c5824f236dfb2b2e8788 --method link_text_after_year
python pull_training_data.py --path $outpath --site-id 6352a28f9a88647dde9064f3 --method link_text_after --method-args="Prior,Step"
python pull_training_data.py --path $outpath --site-id 638faf69def177e79ce4778f --method name_after --method-args="Drug List"
cd $olddir