# sushiro-calendar
## 概要　
あなたは毎週知らされるバイトのシフトをメモするのが面倒になっていませんか？
これを使えばそんなあなたの面倒がいっぺんに解消します！
Google Calendarを使用しているので予定の共有や使っているカレンダーアプリへのインポートも簡単！
これを使えば、シフト管理に革命が起きる！
## JavaScript版使い方

- google clendar APIの設定  
まず、https://developers.google.com/calendar/quickstart/js に従ってgoogle calendar APIの設定を行ってください。  
その時に取得したCLIENT_IDとAPI_KEYをpasswords.jsに書き込んでおいてください。
- ユーザースクリプトの追加  
次にsample.user.jsをコメントに従って書き換えたのち、ブラウザ拡張に導入してください。  
- カレンダーへの追加  
"カレンダーに追加"ボタンを押すと、google calendarに予定が追加されます。

## Python版使い方

- なんの変哲もないただのPython Scriptです。お好みの環境でお使いくださいw
- urls.pyの書き換えと、API登録からのtoken.jsonだけお願いします。
- おすすめの使い方は、スマホのアプリに導入 or exe化してスタートアップに登録です。