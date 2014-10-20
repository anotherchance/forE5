#!C:/Python27/python
# -*- coding: utf-8 -*-

import cgi, cgitb
cgitb.enable()

ACCOUNT = 'hello'
PASSWORD = 'world'

invalid_reply = '''<form enctype="multipart/form-data" action="authorizationE5.py" method="POST" accept-charset="utf-8">
    <fieldset>
        <legend>Please enter login and password</legend>

        <p>
            <label style="text-align:left;">Account</label><br>
            <input type="text" name="account" id="email" size="40" />
        </p>
        <p>
            <label style="text-align:left;">Password</label><br>
            <input  type="text" name="secret" id="web" size="40" />
        </p>
        <p>Account or password was incorrect. Please try again</p>
        <p>
            <input  type="submit" value="Login" />
        </p>
    </fieldset>
</form>
'''

valid_reply = '''<form enctype="multipart/form-data" method="post" action="emarsyscsv.py">
    <fieldset>
    <legend>Please upload csv file</legend>
    <table>
        <tr>
            <td>
                <input type="file" dialogtype="save" value="Choose file" name="choose" required/>
                <input type="submit" value="Upload" name="upload"/>
            </td>
        </tr>
        <tr>
            <td>
                <input type="hidden" name="abspath"/>
            </td>
        <tr/>
    </table>
    </fieldset>
</form>
'''

form = cgi.FieldStorage()

if form['account'].value == ACCOUNT and form['secret'].value == PASSWORD:
    print open('emarsyslabelpattern.html').read().replace('%PAYLOAD%', valid_reply)
    # print open('emarsyslabelpattern.html').read().format(payload=valid_reply)
else:
    print open('emarsyslabelpattern.html').read().replace('%PAYLOAD%', invalid_reply)
    # print open('emarsyslabelpattern.html').read().format(payload=invalid_reply)

