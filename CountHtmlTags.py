import traceback
from logging import getLogger, StreamHandler, DEBUG, FileHandler, Formatter
import os
import codecs
from datetime import datetime
#設定ファイル用のライブラリをインポート
import configparser
#htmlの構造解析ライブラリをインポート
from lxml.html.soupparser import fromstring
#ファイル検索用のライブラリをインンポート
from pathlib import Path

#ログ出力設定
#ログのフォーマット設定
fmt = Formatter("%(asctime)s %(levelname)s %(name)s :%(message)s")
logger = getLogger(__name__)
logger.setLevel(DEBUG)
#コンソール出力用のハンドラー設定
handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(fmt)
logger.addHandler(handler)
#ファイル出力用のハンドラー設定
file_handler = FileHandler("CountHtmlTags.log", mode='a', encoding="UTF-8", delay=False)
file_handler.setLevel(DEBUG)
file_handler.setFormatter(fmt)
logger.addHandler(file_handler)
#親ロガーへのメッセージの伝播をFalseに設定
logger.propagate = False

#メンバ変数定義
tags_count_dic = {}
sorted_tag_list = ()
separator = ""
nowtime = datetime.now().strftime("%Y%m%d%H%M%S")
output_filename = os.path.join("Output", nowtime + "出力結果.txt")

#文字列を改行で区切ってリスト化する関数
def str_list(v):
    return [x for x in v.split("\n") if len(x) != 0]

#ソートできるようにタブの文字列を編集
def checkstr_tag(tag, target_file):
    if isinstance(tag, str):
        return True
    else:
        if target_file != "":
            logger.error("tag解析エラー：" + target_file + " " + str(tag))
        return False

#調査対象のhtmlに含まれる全てのTagの種類を調査する関数
def search_tags(htmlPath):
    try:
        #不正な形式のデータを無視してファイルを読み込む
        with codecs.open(htmlPath, "r", "shift_jis", "ignore") as html:

            xml = fromstring(html.read())
            
            #htmlに含まれるTagの種類を調査
            for x in xml.iter():
                if (x.tag not in tags_count_dic.keys() and checkstr_tag(x.tag, "")):
                    tags_count_dic[x.tag] = 0

    except Exception:
        logger.error("html解析エラー：" + str(htmlPath) + "\n" + traceback.format_exc())

#Tagの種類ごとに件数をカウントする関数
def count_tags(htmlPath, target_file):
    rtn = target_file

    try:
        #不正な形式のデータを無視してファイルを読み込む
        with codecs.open(htmlPath, "r", "shift_jis", "ignore") as html:

            xml = fromstring(html.read())

            #Tagごとの件数をカウント
            for y in xml.iter():
                if checkstr_tag(y.tag, target_file):
                    tags_count_dic[y.tag] = tags_count_dic[y.tag] + 1

            #Tagと件数を出力
            for key in sorted_tag_list:
                rtn = rtn + separator + str(tags_count_dic[key])

            #Tagの件数を初期化
            for key in tags_count_dic.keys():
                tags_count_dic[key] = 0

            return rtn
    except:
        return target_file + separator + "ファイルオープンエラー"

#メイン処理の開始
logger.info("htmlのTagカウント処理　開始")

#設定ファイルの読み込み
settings_conf = configparser.ConfigParser()
settings_conf.read(os.path.join("input","settings.conf"), "UTF-8")

#調査対象のフォルダパス、ファイル名を取得
target_path = Path(settings_conf.get("target", "path"))
target_files = str_list(settings_conf.get("target", "files"))

#出力結果の区切り文字設定を取得
sp_setteing = settings_conf.get("target", "separator")
if sp_setteing == "1":
    separator = "\t"
else:
    separator = ","

#調査対象のフォルダパスの設定がない場合、「.\input\html」を設定
if target_path == "":
    target_path = os.path.join("input", "html")

#調査対象ファイルの設定がない場合、すべてのaspxファイルを検索する
if len(target_files) == 0:
    target_all_files = list(target_path.glob("**/*.aspx"))
    #ファイル名を設定
    for x in target_all_files:
        if x.is_file():
            target_files.append(x.name)

for x in target_files:
    #調査対象ファイルのパスを取得（サブフォルダも調査）
    file_path = list(target_path.glob("**/" + x))

    if len(file_path) == 0:
        logger.error("ファイルが見つかりません。：" + x)
    elif len(file_path) > 1:
        logger.error("同じ名前のファイルが複数あります。：" + x)
    else:
        search_tags(file_path[0])

#Tagをソートして出力するために、ソートされたTagのリストを作成
sorted_tag_list = sorted(tags_count_dic.keys())

#出力先フォルダを作成（作成済みでもエラーとしない）
os.makedirs("Output", exist_ok=True)

with open(output_filename, "w", encoding="UTF-8") as result_file:
    #出力ファイルのヘッダーを書き込み
    line = "ファイル名"
    for tag in sorted_tag_list:
        line = line + separator + tag

    result_file.writelines(line + "\n")

    #出力ファイルに調査結果を書き込み
    for x in target_files:
        file_path = list(target_path.glob("**/" + x))
        if len(file_path) == 0:
            #ファイルが見つからない場合、エラーとして出力
            result_file.writelines(x + separator + "エラー：ファイルが見つかりません。" + "\n")
        elif len(file_path) > 1:
            #同じ名前のファイルが複数ある場合、エラーとして出力
            result_file.writelines(x + separator + "エラー：同じ名前のファイルが複数あります。" + "\n")
        else:
            result_file.writelines(count_tags(file_path[0], x) + "\n")

logger.info("htmlのTagカウント処理　終了")