date=`date +%s`
#date=1727091277
outputs_dir=/data/DataLACP/rambo/outputs
mkdir -p $outputs_dir/hisrag_outputs/$date/cache/s1
mkdir -p $outputs_dir/hisrag_outputs/$date/cache/s2
mkdir -p $outputs_dir/hisrag_outputs/$date/cache/retrieval
mkdir -p $outputs_dir/hisrag_outputs/$date/prediction/s1
mkdir -p $outputs_dir/hisrag_outputs/$date/prediction/s2
mkdir -p $outputs_dir/hisrag_outputs/$date/prediction/valid
mkdir -p $outputs_dir/hisrag_outputs/$date/output/s1
mkdir -p $outputs_dir/hisrag_outputs/$date/output/s2
mkdir -p $outputs_dir/hisrag_outputs/$date/output/retrieval
mkdir -p summary/s1
mkdir -p summary/s1

batch_size=12
max_source_length=512
max_target_length=100
data_dir=/data/DataLACP/rambo/data/come_data #/mnt/ssd2/rambo/data/come_data
output_dir=$outputs_dir/hisrag_outputs/$date/output
res_dir=$outputs_dir/hisrag_outputs/$date/prediction
cache_path=$outputs_dir/hisrag_outputs/$date/cache
task=repo_6
learning_rate=5e-5
devices=3
epoch=10
data_num=-1

his_rag() {
  echo ">>>>>>>>>>>>>>>>>>>> hisrag start"
  CUDA_VISIBLE_DEVICES=$devices \
    python srcnew/hisrag/run_gen.py \
    --do_train --do_eval --do_eval_bleu --do_test --split_tag test\
    --task summarize --sub_task $task --model_type codet5 --data_num $data_num \
    --data_type s2 --num_train_epochs $epoch --warmup_steps 1000 --learning_rate $learning_rate \
    --tokenizer_name=Salesforce/codet5-base --model_name_or_path=Salesforce/codet5-base --data_dir $data_dir \
    --cache_path $cache_path/s2 --output_dir $output_dir/s2 --summary_dir ./summary/s2 \
    --save_last_checkpoints --always_save_model --res_dir $res_dir/s2 \
    --train_batch_size $batch_size --eval_batch_size 8 --max_source_length $max_source_length --max_target_length $max_target_length

}

his_rag

