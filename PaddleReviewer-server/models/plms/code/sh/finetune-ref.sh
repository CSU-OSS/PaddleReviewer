# batch size 6 for 16 GB GPU

mnt_dir="/home/v-zhuoli1/lzzz"

MASTER_HOST=${MASTER_IP} && echo MASTER_HOST: ${MASTER_HOST}
MASTER_PORT=${MASTER_PORT} && echo MASTER_PORT: ${MASTER_PORT}
RANK=${OMPI_COMM_WORLD_RANK} && echo RANK: ${RANK}
PER_NODE_GPU=4 && echo PER_NODE_GPU: ${PER_NODE_GPU}
NODES=1 && echo NODES: ${NODES}
NCCL_DEBUG=INFO

# MASTER_HOST=localhost && echo MASTER_HOST: ${MASTER_HOST}
# MASTER_PORT=23333 && echo MASTER_PORT: ${MASTER_PORT}
# RANK=0 && echo RANK: ${RANK}
# PER_NODE_GPU=1 && echo PER_NODE_GPU: ${PER_NODE_GPU}
# WORLD_SIZE=1 && echo WORLD_SIZE: ${WORLD_SIZE}
# NODES=1 && echo NODES: ${NODES}
# NCCL_DEBUG=INFO

echo -e "import nltk\nnltk.download('punkt')" > tmp.py
python tmp.py

python -m torch.distributed.launch --nproc_per_node ${PER_NODE_GPU} --node_rank=${RANK} --nnodes=${NODES} --master_addr=${MASTER_HOST} --master_port=${MASTER_PORT} ../run_finetune_ref.py  \
  --model_type codet5 \
  --add_lang_ids \
  --train_epochs 30 \
  --config_name ${mnt_dir}/PreViewer/saved_models_codet5_shuai/save_codet5/checkpoints-245000-3.97 \
  --tokenizer_path ${mnt_dir}/PreViewer/pretrained_models/codet5 \
  --model_name_or_path ${mnt_dir}/PreViewer/saved_models_codet5_shuai/save_codet5/checkpoints-245000-3.97 \
  --output_dir ${mnt_dir}/PreViewer/saved_models_ref_shuai_scr \
  --train_filename ${mnt_dir}/Processor/data/ref-train.jsonl \
  --dev_filename ${mnt_dir}/Processor/data/ref-valid.jsonl \
  --max_source_length 200 \
  --max_target_length 200 \
  --train_batch_size 6 \
  --learning_rate 3e-3 \
  --gradient_accumulation_steps 3 \
  --mask_rate 0.15 \
  --save_steps 1800 \
  --log_steps 100 \
  --train_steps 60000 \
  --gpu_per_node=${PER_NODE_GPU} \
  --node_index=${RANK} \
  --seed 2233 \
  --from_scratch \

  # --model_type codet5 \
  # --add_lang_ids \
  # --train_epochs 30 \
  # --config_name ${mnt_dir}/PreViewer/saved_models_codet5_shuai/save_codet5/checkpoints-245000-3.97 \
  # --tokenizer_path ${mnt_dir}/PreViewer/pretrained_models/codet5 \
  # --model_name_or_path ${mnt_dir}/PreViewer/saved_models_codet5_shuai/save_codet5/checkpoints-245000-3.97 \
  # --load_model_path ${mnt_dir}/PreViewer/saved_models_codet5_shuai/save_codet5/checkpoints-245000-3.97 \
  # --output_dir ${mnt_dir}/PreViewer/saved_models_ref_shuai \

  # --model_type t5 \
  # --add_lang_ids \
  # --train_epochs 30 \
  # --config_name ${mnt_dir}/Tufano/pytorch \
  # --tokenizer_path ${mnt_dir}/Tufano/pytorch/TokenizerModel.model \
  # --model_name_or_path ${mnt_dir}/Tufano/pytorch \
  # --output_dir ${mnt_dir}/PreViewer/saved_models_ref_tufano \


  # --model_type codet5 \
  # --add_lang_ids \
  # --train_epochs 30 \
  # --config_name ${mnt_dir}/PreViewer/pretrained_models/codet5 \
  # --tokenizer_path ${mnt_dir}/PreViewer/pretrained_models/codet5 \
  # --model_name_or_path ${mnt_dir}/PreViewer/pretrained_models/codet5 \
  # --output_dir ${mnt_dir}/PreViewer/saved_models_ref_codet5 \

  # --model_type codet5 \
  # --add_lang_ids \
  # --train_epochs 30 \
  # --config_name ${mnt_dir}/PreViewer/pretrained_models/codet5 \
  # --tokenizer_path ${mnt_dir}/PreViewer/pretrained_models/codet5 \
  # --model_name_or_path ${mnt_dir}/PreViewer/pretrained_models/codet5 \
  # --output_dir ${mnt_dir}/PreViewer/saved_models_ref_codet5_simple \
  # --raw_input