
# download text detect model
save_path="inference/det_db"
mkdir -p $save_path
cd $save_path
wget https://paddleocr.bj.bcebos.com/20-09-22/server/det/ch_ppocr_server_v1.1_det_infer.tar
tar xvf ch_ppocr_server_v1.1_det_infer.tar
cd -

# download text recognize model
save_path="inference/rec_crnn"
mkdir -p $save_path
cd $save_path
wget https://paddleocr.bj.bcebos.com/20-09-22/mobile/rec/ch_ppocr_mobile_v1.1_rec_infer.tar
wget https://paddleocr.bj.bcebos.com/20-09-22/server/rec/ch_ppocr_server_v1.1_rec_infer.tar
wget https://paddleocr.bj.bcebos.com/20-09-22/mobile/en/en_ppocr_mobile_v1.1_rec_infer.tar
wget https://paddleocr.bj.bcebos.com/20-09-22/mobile/fr/french_ppocr_mobile_v1.1_rec_infer.tar
wget https://paddleocr.bj.bcebos.com/20-09-22/mobile/ge/german_ppocr_mobile_v1.1_rec_infer.tar
wget https://paddleocr.bj.bcebos.com/20-09-22/mobile/jp/japan_ppocr_mobile_v1.1_rec_infer.tar
wget https://paddleocr.bj.bcebos.com/20-09-22/mobile/kr/korean_ppocr_mobile_v1.1_rec_infer.tar
for file in `ls *.tar`
do
    echo "unzip ${file}"
    tar xvf ${file}
done
cd -
echo "download done"
