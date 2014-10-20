#!C:/Python27/python
# -*- coding: utf-8 -*-
import cgi, cgitb
import os, csv

class CSV:
    '''
    get abs path of input filename
    '''
    def __init__(self, input_filename_abspath, headers):

        self.headers = headers+'\n'
        self.input_filename = os.path.abspath(input_filename_abspath)
        dir, file = os.path.split(self.input_filename)
        self.output_filename = os.path.join(dir, file.split('.')[0]+'_reparsed.'+file.split('.')[1])
        self.inputfile_encoding = self.defineCoding()

    def createFile(self, output_filename_abspath='', encoding='utf8'):
        filename = self.output_filename if output_filename_abspath == '' else output_filename_abspath
        with open(filename, 'w') as output_file:
            output_file.write(self.convertFile().decode(self.inputfile_encoding).encode(encoding))

    def convertRows(self, rownumber=15):
        with open(self.input_filename, 'rb') as inp:
            reader = csv.reader(inp, delimiter=';', quoting=csv.QUOTE_ALL, quotechar='"')
            lines = []
            while rownumber:
                try:
                    row = reader.next()
                except:
                    break
                lines.append(self.convertRow(row))
                rownumber -= 1
        # restore state
        self.is_headers = True
        self. is_end_file = False
        return ''.join(lines)

    def convertFile(self):
        inp = open(self.input_filename, 'rb')
        reader = csv.reader(inp, delimiter=';', quoting=csv.QUOTE_ALL, quotechar='"')
        lines = []
        for row in reader: lines.append(self.convertRow(row))
        # restore state
        self.is_headers = True
        self. is_end_file = False
        return ''.join(lines)

    def convertRow(self, row):
        assert 'convertRaw must be defined!'

    def defineCoding(self, codecs=['cp1251', 'utf8', 'ascii']):
        f = open(self.input_filename)
        test_string = f.readline()
        f.close()
        for i in codecs:
            try:
                test_string.decode(i)
                return i
            except:
                pass

class CSVE5(CSV):
    def __init__(self, input_filename_abspath, headers):
        CSV.__init__(self, input_filename_abspath, headers)
        self.is_headers = True
        self. is_end_file = False

    def convertRow(self, row):

        # case for headers
        if self.is_headers:
            self.is_headers = False
            return self.headers

        # case for end of file
        if row[0] == '': self.is_end_file = True
        # if self.is_end_file: return ','.join(row)+'\n'
        if self.is_end_file: return ''

        # standard convert
        out_row = row[:]
        if out_row[6] == out_row[7]: out_row[7] = ''
        # "title"
        out_row[2] = '"'+out_row[2]+'"'
        # save image
        last = out_row.pop()
        # "outside category > category"
        out_row[4] = 'true' if u'да' in out_row[4].decode(self.inputfile_encoding) else 'false'
        out_row[5] = '"'+out_row[5]+' > '+out_row[6]+'"'
        out_row[6] = last
        return ', '.join(out_row)+'\n'

    def inspect(self):
        for filename in (self.input_filename, self.output_filename):
            print filename.upper()
            cnt = 0
            for line in open(filename).read().splitlines():
                if not line.endswith('jpg'):
                    print line.decode(self.inputfile_encoding)
                    cnt += 1
            print cnt

class CGIForm():
    def __init__(self):
        self.form = cgi.FieldStorage()

    def uploadFile(self, form_name, upload_dir_abspath):
        '''
        creates upload_dir
        creates upload file with filename as in form[file_field].filename
        returns abspath of created file
        '''

        if not form_name in self.form: return
        if os.path.isfile(upload_dir_abspath): return
        if not os.path.isdir(upload_dir_abspath): os.mkdir(upload_dir_abspath)

        try: #need to do on Windows machines
            import msvcrt
            msvcrt.setmode(0, os.O_BINARY) # stdin  = 0
            msvcrt.setmode(1, os.O_BINARY) # stdout = 1
        except ImportError:
            pass

        input_filename = os.path.join(upload_dir_abspath, self.form[form_name].filename)

        f = open(input_filename, 'w')
        f.write(self.form[form_name].file.read())
        f.close()
        return os.path.abspath(input_filename)

    def deleteFile(self, file_to_delete_abspath):
        os.remove(file_to_delete_abspath)
        return

class E5_CSV_CGI(CGIForm, CSVE5):
    def __init__(self):
        '''
        CGIForm: form with all element fields, upload file in pointed dir
        form
        CSVE5: generates outputfilename as default  provides methods to parse uploaded file partly
        input_filename(abspath)
        output_filename(abspath)
        headers
        '''

        self.uploadFolder = 'htdocs'

        CGIForm.__init__(self)

        # All things depends on what page (form) are you coming from
        # The first thing is needed to do id check out action method

        headers = 'item,price,title,link,included,category,image'

        if 'upload' in self.form:
            # uploading file. This script in cgi-bin
            uploaded_file_abspath = self.uploadFile('choose', os.path.join(self.pardir(__file__, 1), self.uploadFolder))
            # headers = 'enter your headers...'
            self.preview_button = '<input type="submit" value="Preview" name="preview"/>'
            self.createlink_button = '<input type="submit" value="Create link" name="createlink"/>'
            self.link = ''
            CSVE5.__init__(self, uploaded_file_abspath, headers)
            self.reply()

        elif 'preview' in self.form:
            uploaded_file_abspath = self.form['abspath'].value
            # headers = self.form['headers'].value
            self.preview_button = '<input type="submit" value="Preview" name="preview"/>'
            self.createlink_button = '<input type="submit" value="Create link" name="createlink"/>'
            self.link = ''
            CSVE5.__init__(self, uploaded_file_abspath, headers)
            self.reply()

        elif 'createlink' in self.form:
            uploaded_file_abspath = self.form['abspath'].value
            # headers = self.form['headers'].value
            self.preview_button = ''
            self.createlink_button = ''
            CSVE5.__init__(self, uploaded_file_abspath, headers)
            link = '/'+os.path.split(self.output_filename)[1]
            self.link = '<tr><td><a href={output} target="_blank" download>  Download file</a></td></tr>'.format(output=link)
            self.createFile()
            self.reply()
            self.deleteFile(self.input_filename)

        # TODO when download button is pushed 1)output is created; 2)output is downloaded; 3) input is deleted
    def reply(self):

        with open('emarsyscsvpattern.html') as pattern:
            print pattern.read().format(text=self.convertRows(),
                                                           input=self.input_filename,
                                                           header=self.headers,
                                                           link=self.link,
                                                           preview_button=self.preview_button,
                                                           createlink_button=self.createlink_button)


    def pardir(self, path, num):
        '''
        return abs path of directory, which is num level upper than path
        '''
        par_path = os.path.dirname(path)
        if num == 0: return par_path
        return self.pardir(par_path, num-1)


if __name__ == '__main__':

    c = CSVE5(r'e:\MICHI_DOWNLOADS\25_09_2014.csv', 'hello')
    c.convertRows()
    c.createFile('hey.csv')
