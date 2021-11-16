import PySimpleGUI as sg
import pathlib
import os
import random
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import arrow

sg.theme('Topanga')
 # -------------- INITIALIZING VARIABLES ---------------------
global word
lines = []
fn = ''
myList = []
vocabulary = []
meaning = ''
your_answer = ''
voc_file = None
txt_file = None
tra_file = None
exmpl_file = None
german = ''
english = ''
flip = 1
flag_date = 0
sz = (12,1)
correct = 0
score = 0
right = 0
wrong = 0
score_Wrong = 0
score_Right = 0
number_of_questions = 0
to_date = arrow.now().format('DD-MM-YYYY')

headers = {"Referer" : "https://www.google.com", "User-Agent" : "Mozilla/5.0"}


#------------------ DEFINING THE BUTTONS -------------------
column1 = [ # these are buttons
            [sg.Button('LOAD_VOC', enable_events=True, size=sz, button_color="#056490"), ],
            [sg.Button('SAVE_VOC', enable_events=True, size=sz, button_color='#12917A')],
            [sg.Button('SORT', enable_events=True, size=sz, button_color='#0B5502')],
            [sg.Button('CLR-VOC', size=sz, button_color='brown')]
            ]

column2 = [ # buttons
            [sg.Button('LOAD_TXT', enable_events=True, size=sz, button_color="#056490")],
            [sg.Button('SAVE_TXT', enable_events=True, size=sz, button_color='#12917A')],
            [sg.ReadButton('CLR-TXT', size=sz, button_color="brown")],
            [sg.ReadButton('NOTES', size=sz, button_color='#5c5c8a')]
            ]
column3 = [ # buttons
            [sg.Button('LOAD_TRAN', enable_events=True, size=sz, button_color="#056490")],
            [sg.Button('SAVE_TRAN', enable_events=True, size=sz, button_color='#12917A')],
            [sg.ReadButton('CLR-TRAN', size=sz, button_color='brown')]
            ]

column4 = [[sg.ReadButton('Langenscheidt', pad=(20,0))]] # buttons for dictionaries
#column5 = [[sg.ReadButton('Glosbe')]]
#column6 = [[sg.ReadButton('FreeDictionary')]]
column7 = [[sg.ReadButton('Collins')]]

# -------------- THE RIGHT COLUMN ----------------------
right_col_bottom = [
            [sg.Text("SEARCH ONLINE DICTIONARIES", pad=(10,0), font=(14,17))],
            [sg.InputText(size=(30,2), focus=True, do_not_clear=False, font='12', key='word', background_color='black', pad=(10,0))],
            [sg.Column(column4, pad=0), sg.Column(column7)]
            ]

right_col_top = [
                [sg.Text('EXAMPLE SENTENCES', font=(12))],
                [sg.Multiline(size=(68,8), font='Tahoma 12', key='-EXAMPLES-', autoscroll=True)],
                [sg.ReadButton('Collins-Examples'), sg.ReadButton('Save Examples', size=sz, button_color='#12917A'), sg.ReadButton('CLEAR', size=sz, button_color='brown')]
            ]
right_col_mid = [
                [sg.Text('Take a Vocabulary Test from File: ', font='Tahoma 14'), sg.ReadButton('Choose File'), sg.ReadButton('Flip Sentences', button_color='#666633')],
                [sg.Text('File is: ', key='addFLN')], # -------
                [sg.Multiline(size=(68,6), font='Tahoma 13', key='test-sentence', autoscroll=True)],
                [sg.Text('Type your answer below and then PRESS the ENTER key', font='Tahoma 14')],# sg.ReadButton('Click here to Confirm your Answer')],
                [sg.Input(size=(55,2), enable_events=True,background_color='black', font='13', text_color='white', key='answer')],
                [sg.Button('Submit', visible=False, bind_return_key=True)],
                [sg.Button('Next Word', enable_events=True, visible=True), sg.Text('Score: ', key='score')]
            ]
#------------------- THE LAYOUT-------------------
layout = [
    # HORIZONTAL ARRANGEMENT OF ELEMENTS
         [sg.Text("Vocabulary Box", enable_events=True, key='add')],
         [sg.Multiline(size=(55,10), font='Tahoma 13', key='vocab', autoscroll=True), sg.Column(column1), sg.VerticalSeparator(pad=None), sg.Column(right_col_top)],
        
         [sg.Text("Study Text Box")],
         [sg.Multiline(size=(55,9), font='Tahoma 13', key='-STUDY-', autoscroll=True), sg.Column(column2), sg.VerticalSeparator(pad=None), sg.Column(right_col_mid)],

         [sg.Text("Translation Box")],
         [sg.Multiline(size=(55,9), font='Tahoma 13', key='-TRAN-', autoscroll=True), sg.Column(column3), sg.VerticalSeparator(pad=None), sg.Column(right_col_bottom)]
         ]
        
window = sg.Window("TbLLT Program", layout, location=(0,0), resizable=True, finalize=True)

# ---------------------- SAVE OPERATIONS -----------
def save_voc_file(file):
    if voc_file:
        voc_file.write_text(values['vocab']) # save the vocabulary  
    else:
        save_voc_file_as()

def save_txt_file(file):    
    if txt_file:
        txt_file.write_text(values['-STUDY-']) # save the study text
    else:
        save_txt_file_as()

def save_tra_file(file):    
    if tra_file:
        tra_file.write_text(values['-TRAN-']) # save the study text
    else:
        save_tra_file_as()
    #------------- SAVE AS OPERATIONS ---------
def save_voc_file_as():
    global voc_file, voc_pathname
    voc_pathname = sg.popup_get_file('', save_as=True, no_window=True)
    if voc_pathname:
        voc_file = pathlib.Path(voc_pathname)
        voc_file.write_text(values['vocab'])
        return voc_file

def save_txt_file_as():
    global txt_file
    txt_fn = sg.popup_get_file('', save_as=True, no_window=True)
    if txt_fn:
        txt_file = pathlib.Path(txt_fn)
        txt_file.write_text(values['-STUDY-'])
        return txt_file

def save_tra_file_as():
    global tra_file
    tra_fn = sg.popup_get_file('', save_as=True, no_window=True)
    if tra_fn:
        tra_file = pathlib.Path(tra_fn)
        tra_file.write_text(values['-TRAN-'])
        return tra_file

def save_examples():
    with open('saved-examples.txt', 'a+') as file:
        file.write(values['-EXAMPLES-'])
# ----------------- LOAD FILES ---------------------
def load_voc_file():
    global voc_file, voc_pathname, strVocPath, flname, fn
    voc_pathname = sg.popup_get_file('', no_window=True)
    with open(voc_pathname, 'r') as file:
        readVoc = file.read()
        window['vocab'].update(readVoc)
        strVocPath = str(voc_pathname) # convert path to string
        flname = strVocPath.split('/') # split on fw slash
        fn = flname[-1] # this is the voc file name
        window['add'].update("Vocabulary: "+fn)
    #file.close()

def load_txt_file():
    global txt_file
    txt_fn = sg.popup_get_file('', no_window=True)
    with open(txt_fn, 'r') as file:
        readTxt = file.read()
        window['-STUDY-'].update(readTxt)
    #file.close()

def load_tra_file():
    global tra_file
    tra_fn = sg.popup_get_file('', no_window=True)
    with open(tra_fn, 'r') as file:
        readTra = file.read()
        window['-TRAN-'].update(readTra)
    #file.close()

def load_test():
    global test_file, test_pathname, english, german, readTest, length
    global fileNm, strTestPath, fname
    test_pathname = sg.popup_get_file('', no_window=True)
    with open(test_pathname, 'r') as file:
        readTest = file.readlines()
        length = len(readTest)
        strTestPath = str(test_pathname)
        fileNm = strTestPath.split('/')
        fname = fileNm[-3:]
        window['addFLN'].update('File is: ' + str(fname))
    display_word()

def display_word():
    global english, german, readTest, num
    num = random.randint(0, length-1)
    
    try:
        
        if flip%2 == 1: # odd numbered sentences
            german = readTest[num].split(' = ')[0]
            english = readTest[num].split(' = ')[1]

            window['test-sentence'].Update('please translate: ' + '\n' + '--> '+ german)
            window['answer'].set_focus
            
        else: # even numbered sentences
            window['test-sentence'].Update('')
            german = readTest[num].split(' = ')[1]
            english = readTest[num].split(' = ')[0]
            window['test-sentence'].print('Please translate the following: ' + '\n' + '--> ', german)
            window['answer'].set_focus
            print('flip: ', flip)

    except:
        IndexError
    
# ---------- CHECK ANSWERS ------------------
def check_answer():
    global english, your_answer, number_of_questions, right
    global score, wrong, score_Right, score_Wrong
    number_of_questions += 1
    your_answer = values['answer']
    
    if your_answer in english:
        right += 1
        score_Right = round((right / number_of_questions) * 100)
        score = str(score_Right)
        window['test-sentence'].print('\n'+ '*** CONGRATULATIONS: Correct Answer ***' + '\n' + english)

    else:
        score_Right = round((right / number_of_questions) * 100)
        score = str(score_Right)
        #window['test-sentence'].print('\n'+'Sorry, the correct answer is: '+ english)
        window['test-sentence'].print('\n'+'You wrote: '+your_answer+'\n'+'The correct answer is: '+english)
    window.find_element('answer').Update('')
    window.find_element('score').Update('Score: '+score+'%')
    
# # -------------------- SORT -----------------
def default(vocabulary):
    l = vocabulary[:]
    l.sort()
    display_list(l)

def display_list(list):
    global list_displayed, voc_pathname
    list_displayed = list
    values = [l for l in list]
    separator = "\n"
    window['vocab'].print(separator.join(values))

# --------------- NEW WINDOW, POP-UP: NOTES  -------------
def open_window():
    global to_date, flag_date
    flag_date += 1
    print('flag_date: ', flag_date)
    layout = [[sg.Text("Take notes below", key="new")],
    [sg.Multiline(size=(60,20), background_color='black', text_color='white', focus=True, key='notes')],
    [sg.ReadButton('Save_Notes', size=(12,1))]]
    # ------------------- Open notesGUI file when window loads ---------
    with open('/Users/georgiostrialonis/Desktop/FLANG/notesGUI.txt', 'r') as file:
        content = file.read()
        #print(content+' opend file')

    def save_notes():
        with open('/Users/georgiostrialonis/Desktop/FLANG/notesGUI.txt', 'w') as fl:
            fl.write(values['notes'])

    window = sg.Window("Notes", layout, modal=True, location=(800,30), finalize=True)
    if flag_date > 1:
        to_date = ''
    else:
        to_date = to_date

    window['notes'].print(to_date + '\n' + content)

    while True:

        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == 'Save_Notes':
            save_notes()

    window.close()
'''---------------- THE LOOP -------------------'''
while True:
    event, values=window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'SAVE_VOC':
        save_voc_file(voc_file)
    
    if event == 'SAVE_TXT':
        save_txt_file(txt_file)
    
    if event == 'SAVE_TRAN':
        save_tra_file(tra_file)

    if event == 'SORT':
        global voc_pathname
        dirname, filename = os.path.split(os.path.abspath(__file__))
        pathname = voc_pathname
        vocabulary = [line.strip() for line in open(pathname)] # the text file as a list    
        window.find_element('vocab').Update('')
        default(vocabulary)
# ----------- WEB SCRAPING ---------------
    '''------------------- LANGENSCHEIDT -------------'''
    if event == 'Langenscheidt': 
    
        url = "https://en.langenscheidt.com/german-english/"+values['word']
        #meaning = None
        myList = []
        response = requests.get(url, headers=headers).text
        soup = BeautifulSoup(response, "html.parser")

        for transl in soup.find_all('a', class_='blue'):
            myStr = transl.find('span', class_='btn-inner').text
            article = soup.find('span', class_='full').text
            if article == 'Femininum | feminine':
                article = 'die'
            elif article == 'Maskulinum | masculine':
                article = 'der'
            elif article == 'Neutrum | neuter':
                article = 'das'
            else:
                article == ''
            myStr = myStr.strip()
            
            myList.append(myStr)
            s = ', '
            meaning = s.join(myList)
            
        window['vocab'].print(values['word'] +', '+article+' = '+meaning)

    ''' ---------------------- COLLINS WORD SEARCH -----------------'''
    if event == 'Collins':

        url = "https://collinsdictionary.com/dictionary/german-english/"+values['word']
        myList = []
        try:
            response = requests.get(url, headers=headers).text
            soup = BeautifulSoup(response, "html.parser")

            for trans in soup.find_all('span', class_='cit'):
                myStr = trans.text
                article = soup.find('span', class_='pos').text
                if 'masculine' in article:
                    article = 'der'
                elif 'feminine' in article:
                    article = 'die'
                elif 'neuter' in article:
                    article = 'das'
                else:
                    article = ''
                myStr = myStr.strip() # removes brackets and quotations
                myList.append(myStr)
                s = ', '
                meaning = s.join(myList)
        except:
            UnicodeDecodeError,
            NameError
        window['vocab'].print(values['word'] + ', ' + article + ' = ' + meaning)

    '''------------- COLLINS EXAMPLES SEARCH ---------'''

    if event == 'Collins-Examples':
        headers = {'Referer': 'https://www.google.com', 'User-Agent': 'Mozilla/5.0'}
        exmplList = []
        url = "https://collinsdictionary.com/dictionary/german-english/"+values['word']

        response = requests.get(url, headers=headers).text
        soup = BeautifulSoup(response, 'html.parser')

        for example in soup.find_all('div', class_='cit type-example'):
            german = example.find('span', class_='quote').text
            english = example.find('span', class_='cit type-translation quote').text
            exmpl = german + ' = ' + english
            exmplList.append(exmpl)
            
        for i in range(len(exmplList)):
            window['-EXAMPLES-'].print(exmplList[i], end='\n')

    if event == 'CLEAR':
        window.find_element('-EXAMPLES-').Update('')

# ---------- LOADING VOCABULARY, STUDY TEXT, TRANSLATION ---------
    if event == 'LOAD_VOC':
        load_voc_file()

    if event == 'LOAD_TXT':
        load_txt_file()

    if event == 'LOAD_TRAN':
        load_tra_file()
# ------------- CLEAR --------------------

    if event == 'CLR-VOC':
        window.find_element('vocab').Update('')
    if event == 'CLR-TXT':
        window.find_element('-STUDY-').Update('')
    if event == 'CLR-TRA':
        window.find_element('-TRAN-').Update('')

    # ---------------------EXAMPLES SAVE ------------
    if event == 'Save Examples':
        save_examples()
    # ---------------- TEST AREA --------------------
    if event == 'Choose File':
        load_test()
    if event == 'Submit': # this is for the hidden button
        window['answer'].set_focus
        check_answer()
        
    if event == 'Next Word':
        display_word()
        #window.find_element('answer').SetFocus
        
        
    #---- Create a function from the lines below ---

    if event == 'Flip Sentences':
        flip += 1
        if test_pathname == '':
            window['test-sentence'].update('Please select file first!')
        else:
            display_word()

    if event == 'NOTES':
        open_window()
       
window.close()

      