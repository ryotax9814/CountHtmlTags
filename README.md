# CountHtmlTags
* 概要
    * htmlファイルに含まれるTagの種類ごとの件数をカウントします。
* 実行環境
    * Python 3.6.5
    * lxml 4.2.1
    * beautifulsoup4 4.6.3
* 使い方
    1. /Input/html に調査対象のhtmlファイルを格納します。
        * サブディレクトリまで検索するため、特にフォルダ構成の指定はありません。
    2. /Input/settings.conf を開き、設定内容を確認します。
    3. CountHtmlTags.py を実行します。
        * 出力結果は /Output に出力されます。
        * CountHtmlTags.log がログファイルです。
