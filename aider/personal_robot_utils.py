from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from threading import Thread

import pyautogui as pya
import pyperclip
import glob
import os
import sys
import time
import re

from datetime import datetime as dt
from datetime import timedelta

from lxml import etree



from colorama import init
from colorama import Fore, Back, Style
init()


DEFAULT_FOLDER = r"D:\DEV\sportbet\bet"
IMG_FOLDER = r"D:\DEV\sportbet\images\_generic"
HTML_FILE = r"D:\DEV\sportbet\bet\20210921_220720-bet365_inicio.html"

if not os.path.exists(DEFAULT_FOLDER):
    DEFAULT_FOLDER = DEFAULT_FOLDER.replace("D:", "C:")
    HTML_FILE = HTML_FILE.replace("D:", "C:")

IMG_WIN_GUARDAR_BTN = os.path.join(IMG_FOLDER, "win_guardar_btn.png")
IMG_WIN_GUARDAR_TITLE = os.path.join(IMG_FOLDER, "win_guardar_title.png") ## Borde en bet365 cuando se hace una bÃºsqueda en chrome
IMG_CHROME_ADDONMENU_EXP = os.path.join(IMG_FOLDER, "chrome_Addon_Menu_expanded.png")
IMG_CHROME_REFRESHPAGE_ICON = os.path.join(IMG_FOLDER, "chrome_refresh_page_icon.png")

def scrollToElement(br, elem, scroll=0):
    """scroll: with -integer goes up, with +integer gets down"""
    br.execute_script("arguments[0].scrollIntoView();", elem)
    if scroll:
        br.execute_script("window.scrollBy(0,{})".format(scroll))

def scrollDownPage(br, sleep_time=1):
    try:
        print("time.sleep(", sleep_time)
        time.sleep(sleep_time)
        #seeMore = br.find_element_by_class_name('uiMorePagerPrimary')
        #seeMore.click()
        br.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    except Exception as e:
        print(e)
    print("Done scrolldown!")


def waitUntil(br, expression="//a", delay=3, click=False, by_method=By.XPATH, all=False):
    try:
        elem = WebDriverWait(br, delay).until(EC.element_to_be_clickable(
        (by_method, expression)))
        if click:
            elem.click()
        if all:
            elems = br.find_elements(by_method, expression)
            return elems
        else:
            return elem
    except Exception as e:
        print(Fore.RED, "Not found element {}".format(expression), Fore.RESET)
        return False


###############################################################
## https://ben.land/post/2021/04/25/windmouse-human-mouse-movement/
import numpy as np
import random
sqrt3 = np.sqrt(3)
sqrt5 = np.sqrt(5)

def wind_mouse(start_x, start_y, dest_x, dest_y, G_0=9, W_0=3, M_0=15, D_0=12, move_mouse=lambda x,y: None):
    '''
    WindMouse algorithm. Calls the move_mouse kwarg with each new step.
    Released under the terms of the GPLv3 license.
    G_0 - magnitude of the gravitational fornce
    W_0 - magnitude of the wind force fluctuations
    M_0 - maximum step size (velocity clip threshold)
    D_0 - distance where wind behavior changes from random to damped

    https://ben.land/post/2021/04/25/windmouse-human-mouse-movement/
    '''
    current_x,current_y = start_x,start_y
    v_x = v_y = W_x = W_y = 0
    while (dist:=np.hypot(dest_x-start_x,dest_y-start_y)) >= 1:
        W_mag = min(W_0, dist)
        if dist >= D_0:
            W_x = W_x/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
            W_y = W_y/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
        else:
            W_x /= sqrt3
            W_y /= sqrt3
            if M_0 < 3:
                M_0 = np.random.random()*3 + 3
            else:
                M_0 /= sqrt5
        v_x += W_x + G_0*(dest_x-start_x)/dist
        v_y += W_y + G_0*(dest_y-start_y)/dist
        v_mag = np.hypot(v_x, v_y)
        if v_mag > M_0:
            v_clip = M_0/2 + np.random.random()*M_0/2
            v_x = (v_x/v_mag) * v_clip
            v_y = (v_y/v_mag) * v_clip
        start_x += v_x
        start_y += v_y
        move_x = int(np.round(start_x))
        move_y = int(np.round(start_y))
        if current_x != move_x or current_y != move_y:
            #This should wait for the mouse polling interval
            move_mouse(current_x:=move_x,current_y:=move_y)
    return current_x,current_y
###############################################################

def _exampleUsingWindMouse():
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=[13,13])
    plt.axis('off')
    plt.jet() # plt.autumn(), inferno(), .gray()
    for i, y in enumerate(np.linspace(-200,200,25)):
        plt.annotate(i, (-5,y))
        # G_0=9, W_0=3, M_0=15, D_0=12 default
        G_0=9+random.randrange(int(-9/2),int(9/2))
        W_0=3+random.randrange(int(-3/3),int(3/2))
        M_0=15+random.randrange(int(-15/2),int(15/4))
        D_0=12+random.randrange(int(-12/2),int(12/4))
        print(f"line {i}:",G_0, W_0, M_0, D_0, "G_0, W_0, M_0, D_0")
        points = []
        wind_mouse(0,y,500,y,move_mouse=lambda x,y: points.append([x,y]))
        points = np.asarray(points)
        plt.plot(*points.T)
    plt.xlim(-50,550)
    plt.ylim(-250,250)
    plt.show()


def moveToText(br, search_text="", nearTopLeft=False, speed=10, click=True, top_adjust=-40):
    ### # TODO: similar to moveToWE()
    pass

def moveToWE(br, webelement, search_text="", nearTopLeft=False, speed=10, click=True, top_adjust=-40):
    activateChromeWindow()
    window = getActiveWindow()
    if window:
        window.maximize()
    pya.press(["pageup"]*5)
    userBrowserSearch(search_text)
    activateSeleniumWindow()
    pya.press(["pageup"]*5)
    brBrowserSearch(search_text)
    box = getElementBoxOnScreen(br, webelement, top_adjust=top_adjust)
    if box:
        coords = xyInsideBox(box)
        print("box:", box, "\ncoords odds:", coords)
        print("Buscando texto: ", search_text, " texto del webelement:", webelement.text)
        #print(webelement.find_element(By.XPATH, "./../..").get_attribute("innerHTML"))
        #print(webelement.find_element(By.XPATH, "./../..").text)
        activateChromeWindow()
        p = xyInsideBox(box, nearTopLeft=nearTopLeft)
        moveToH(*p, speed=speed)
        if click:
            clickH()
        return p

def moveTo(*arg, **kwargs):
    """A veces cambio de moveToH() to moveTo() y me olvido de poner el "pya." antes """
    pya.moveTo(*arg, **kwargs)

def moveToH(x, y, speed=5):
    """https://ben.land/post/2021/04/25/windmouse-human-mouse-movement/
    speed=(1 slow () to 10 quick, less than 0.4)
    """
    if speed < 4:
        speed = 4
    elif speed > 1:
        speed = 10
    delay = (10-speed)/20

    x0, y0 = pya.position()
    G_0 = 9+random.randrange(int(-9/2),int(9/2))
    W_0 = 3+random.randrange(int(-3/3),int(3/2))
    M_0 = 15+random.randrange(int(-15/2),int(15/4))
    D_0 = 12+random.randrange(int(-12/2),int(12/4))
    points = []
    wind_mouse(x0, y0, x, y, move_mouse=lambda x,y: points.append([x,y]))
    r_x0 = 60
    r_y0 = 60
    i = 1
    num_points = len(points)
    min_steps = int(min(num_points/20, 2))+1
    max_steps = int(min(num_points/10, 4))+2
    try:
        steps = sorted(random.choices(range(len(points[:-5])), k=random.randrange(min_steps,max_steps)))
    except IndexError:
        steps = []
    for idx in steps:
        p = points[idx]
        i += 1
        #print(r_x0, r_y0)
        r_x = random.randrange(-r_x0,r_x0)
        r_y = random.randrange(-r_y0,r_y0)
        step_delay = (i+delay)/10+(random.random()/speed)
        pya.moveTo(p[0]+r_x,p[1]+r_y, step_delay )
        r_x0 = abs(r_x)+1
        r_y0 = abs(r_y)+1
    if len(points):
        p = points[-1]
        step_delay = delay+(random.random()/speed)
        pya.moveTo(p[0],p[1], step_delay, pya.easeOutQuad)
    pya.sleep(0.3+random.random()/speed) # A human waits a little after reach a point

def clickH():
    """
    Clicks humanos duran entre 50 y 200 ms.
    Testeado con:

    <!DOCTYPE html>
    <html lang="es">
      <head>
        <title>Test Human Clicks </title>
        <link rel="stylesheet" href="css/estilos.css" />
      </head>
      <body>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script>
    $(document).ready(function() {
      // CÃ³digo jQuery
      var start_time;
        function start() {
            start_time = new Date();
        }
        function end() {
            var now = new Date();
            alert(now-start_time);
        }

        $('body,html').mousedown(start);
        $('body,html').mouseup(end);

    });
    </script>
      <h1>How long does a click last?</h1>
      <div id='element_id'>
        TEST CLICKING HERE
       </div>
      </body>
    </html>

    """
    ##pya it is a bit slow so we use 5-90
    ms = random.randrange(5,90)/1000
    pya.mouseDown()
    pya.sleep(ms)
    pya.mouseUp()
    print(ms)


def hasSpetialChars(text):
    regexp = re.compile('[^0-9a-zA-Z .,-_]+')
    if regexp.search(text):
        return(True)
    else:
        return(False)


def typeH(text):
    """Write text as a human
    TODO: Improve
          Mistake and correct sometimes
    """
    if hasSpetialChars(text):
        ## Just CopyPaste
        pyperclip.copy(text)
        pya.hotkey("ctrl", "v")
    else:
        ## Typing like a human
        try:
            steps = set(random.choices(range(3,len(text)-1),k=random.randrange(int(len(text)/2))+1 ) )
        except:
            steps = set([0,len(text)])
        steps = sorted(list(steps))
        idx = 0
        #print(steps)
        for s in steps:
            substr = text[idx:s]
            #print(idx, s, substr)
            pya.write(substr, interval=(0.1+random.random())/10)
            idx=s
        substr = text[idx:]
        #print(idx, s, substr)
        pya.write(substr, interval=(0.2+random.random())/10)


def xyInsideBox(box, nearTopLeft=False):
    """ Get an random XY inside a pyscreeze.Box
        nearTopLeft: False, gets a more or less centered point
        nearTopLeft: True, gets a point near topleft
    """
    mu, sigma = 0, 0.1 # mean and standard deviation
    dx, dy = np.random.normal(mu, sigma, 2)
    if not nearTopLeft:
        dx = int(dx * (box.width-2))
        dy = int(dy * (box.height-2))
        center = pya.center(box)
        x = center.x+dx
        y = center.y+dy
    else:
        dx = int(abs(dx) * max((box.width/10), 10) )
        dy = int(abs(dy) * max((box.height/4), 10) )
        x = 5+box.left + dx
        y = 5+box.top + dy

    return (x, y)

def getUrl():
    #https://stackoverflow.com/questions/52675506/get-chrome-tab-url-in-python
    activateChromeWindow()
    with pya.hold("ctrl"):
        pya.press("l")  #  equivalente a "f6"
    pya.sleep(0.3)
    pya.hotkey('ctrl', 'c') # for copying the selected url
    import pyperclip # pip install pyperclip required
    url = pyperclip.paste()
    return url

def openUrl(url):
    pya.sleep(1)
    with pya.hold("ctrl"):
        pya.press("l")  #  equivalente a "f6"
    pya.write(url)
    pya.sleep(0.2)
    pya.press("enter")
    pya.sleep(0.2)
    found = waitUntilLocateImage(IMG_CHROME_REFRESHPAGE_ICON, delay=1, tries=10)
    print(found)
    pya.sleep(1)


def activateChromeWindow(with_text="", launch_if_any=False, navigator="Chrome"):
    return activateNavigatorWindow(with_text=with_text,
        launch_if_any=launch_if_any,
        navigator="Chrome")

def activateNavigatorWindow(with_text="", launch_if_any=False, navigator="Chrome"):
    """
    navigator="Chrome" or "Firefox"
    """
    navigator = navigator.title()

    with_text = with_text.upper()
    win = pya.getActiveWindow()
    if win and win.title.endswith(f" {navigator}") and with_text in win.title.upper():
        return win
    wins = pya.getAllWindows()
    found_window = False

    chrome_found = False
    for i, win in enumerate(wins):
        if win.title.endswith(f" {navigator}"):
            chrome_found = True
            break
    if not chrome_found and launch_if_any:
        import webbrowser
        if navigator.title() == "Firefox":
            firefox_path = os.path.join("C:", "Program Files (x86)", "Mozilla Firefox", "firefox.exe")
            webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefox_path))
        a = startChronometer("Open "+navigator)
        if navigator == "Firefox":
            webbrowser.get("firefox").open_new('http://')
        else:
            webbrowser.open_new('http://')
        if navigator == "Firefox":
            confidence = 0.72
            #TODO coger una imagen de Firefox
        
        try:
            waitUntilLocateImage(IMG_CHROME_REFRESHPAGE_ICON, confidence=0.72)
        except Exception as e:
            #Refresh page with pya f5
            pya.press("f5")   
        stopChronometer(a)

    for i, win in enumerate(wins):
        if win.title.endswith(f" {navigator}") and with_text in win.title.upper():
            found_window = win
            break

    try:
        if found_window:
            found_window.activate()
            return found_window
        else:
            return False
    except Exception as e:
        print(f"activateNavigatorWindow: Error at found_window.activate(): {e}")
        return False

def activateSaveAsWindow():
    titles = ["Guardar como","Save as"]
    wins = pya.getAllWindows()
    found_window = False
    for i, win in enumerate(wins):
        if found_window:
            found_window.activate()
            return found_window
        for i_title in titles:
            if win.title.startswith(i_title):
                found_window = win
                break
    return False

def activateSeleniumWindow():
    win = pya.getActiveWindow()
    if win.title.startswith("AUTO_SPORTBET"):
        return win
    wins = pya.getAllWindows()
    found_window = False
    for i, win in enumerate(wins):
        if win.title.startswith("AUTO_SPORTBET"):
            found_window = win
            break
    if found_window:
        found_window.activate()
        return found_window
    else:
        return False


def getActiveWindow():
    return pya.getActiveWindow()


def isActiveWindow(contains_text="bet365"):
    act_win_title = pya.getActiveWindow().title
    if act_win_title.lower().find(contains_text.lower()) > -1 and \
        (act_win_title.endswith("Google Chrome") or \
         act_win_title.endswith("Edge") or \
         act_win_title.endswith("Firefox")):
        return True
    else:
        return False


def saveToFile(data, filename, key="data"):
    """
    https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
    """
    import json

    iterable = True
    try:
        len(data)
    except TypeError as e:
        iterable = False
        data = data.__dict__
    try:
        data_dict = {key: data} ## Avoid problems of serialization
        just_test = json.dumps(data_dict)
    except TypeError as e:
        print()
        ## TypeError: Object of type LiveWinnerOdd??? is not JSON serializable
        new_data = {}
        for k,v in data.items():
            new_data[k] = k,v.__dict__
        data_dict = {key: new_data} ## Avoid problems of serialization

    json_data = json.dumps(data_dict, indent=4, sort_keys=True)
    with open(filename, 'w') as file:
         file.write(json_data) # use `json.loads` to do the reverse


def readFromFile(filename, key="data"):
    import json
    with open(filename, "r") as file:
        #json_data = json.loads(file.read())
        json_data = json.load(file)
    if key:
        json_data = json_data[key]
    return json_data


def userBrowserSearch(text):
    activateChromeWindow()
    pya.sleep(1)
    with pya.hold('ctrl'):
        pya.press(['f'])
    pya.sleep(1)
    typeH(text)


def brBrowserSearch(text, maximize=True):
    win = activateSeleniumWindow()
    if not win:
        return False
    if win and maximize:
        win.maximize()
    pya.sleep(0.3)
    with pya.hold('ctrl'):
        pya.press(['f'])
    pya.sleep(0.3)
    typeH(text)

from difflib import SequenceMatcher
def textSimilarity(a, b, mix_words=True):
    """ TODO a veces cambian de orden apellido y nombre
    """
    return SequenceMatcher(None, a, b).ratio()


def waitUntilLocateImages(imgs, delay=3, tries=2, confidence=0.8, method="any", randomMove=False, msgs=[], region=None, silent=True):
    """ Busca las imagenes 'imgs' indicadas haciendo los reintentos indicados.
        Devuelve False si no encuentra ninguna, o una o varias coordenas en caso de encontrar.
        method = "any" si aparece cualquiera devuelve la primera coordenada de la imagen encontrada,
                 "all" devuelve todas las coordenadas de las imÃ¡genes
    """
    found = {}
    for i in range(len(imgs)):
        found[i] = False
    for i in range(tries):
        for j, img in enumerate(imgs):
            msg = ""
            if len(msgs) == len(imgs):
                msg = msgs[j]
            if not silent:
                print("\n",Fore.CYAN, "Intento:", i, "Imagen:", j, Fore.RESET, "\n")
                print(Fore.YELLOW, f"waitUntilLocateImages - img{j}[{msg}]  try: {i}", Fore.RESET)
            p = waitUntilLocateImage(img, delay=delay, tries=1, confidence=confidence, randomMove=randomMove, msg=msg, region=region, silent=silent)
            if p:
                found[j] = p
            if found[j] and method == "any":
                if not silent:
                    print(Fore.GREEN, f"Found {msg}!!", Fore.RESET, p)
                return p
        if np.all(list(found.values())):
            return found
    return False

def waitUntilLocateImage(img, delay=1, tries=5, confidence=0.8, randomMove=False, msg="", region=None, silent=True):
    """Espera a que aparezca algo en pantalla. Util para esperar diÃ¡logos como el GuardarComo... """
    if randomMove:
        delay = delay/3
    for i in range(tries):
        found = pya.locateOnScreen(img, confidence=confidence, region=region)
        if found:
            p = xyInsideBox(found, nearTopLeft=False)
            return p
        if not silent:
            print(f"waitUntilLocateImage[{msg}] {(i+1)}/{(tries)}")
        if randomMove:
            ## Makes some random move...
            moveToH(100, random.randrange(200,600), speed=10)
            pya.press("esc")
        if stopableSleep(delay, silent=silent):
            return None
    return None

def waitWhileImageExists(img, delay=0.3, tries=10, confidence=0.8, randomMove=False, msg="", region=None):
    """Espera a que aparezca algo desaparezca de la pantalla.
       Ãštil para esperar que se acaben procesamientos...
       Returns True when "img" is not on the screen, or disappears.
       Returns False when "img" is still on the screen after the number of tries.
    """
    for i in range(tries):
        found = pya.locateOnScreen(img, confidence=confidence, region=region)
        if found:
            p = xyInsideBox(found, nearTopLeft=False)
            print(f"Image[{msg}] exists, so waiting {(i+1)}/{(tries)}")
            stopableSleep(delay)
        else:
            return True
        if randomMove:
            ## Makes some random move...
            moveToH(random.randrange(300,500), random.randrange(200,600))
    return False


def closeAnySaveAsDialog():
    max_tries = 5
    while activateSaveAsWindow() and max_tries:
        max_tries -= 1
        closeSaveAsDialog()

def closeSaveAsDialog():
    found1 = waitUntilLocateImage(IMG_WIN_GUARDAR_TITLE, delay=1,
                        tries=1, confidence=0.7, msg="IMG_WIN_GUARDAR_TITLE")
    found2 = waitUntilLocateImage(IMG_WIN_GUARDAR_BTN, delay=1,
                        tries=1, confidence=0.7, msg="IMG_WIN_GUARDAR_BTN")
    if found1 and found2:
        print(Fore.CYAN, "closeSaveAsDialog() esc", Fore.RESET)
        pya.press("esc")
        pya.sleep(1)


def closeExpandedChromeAddonMenu():
    """ Devuelve si el menu estÃ¡ abierto"""
    """ A veces estÃ¡ desactivada la extension y se ve en gris """
    top_row = getRegionInScreen(num_rows=2,row=0)
    found = waitUntilLocateImage(IMG_CHROME_ADDONMENU_EXP, confidence=0.7, delay = 0.2, tries=2, region=top_row)
    if found:
        activateChromeWindow()
        print("Detected IMG_CHROME_ADDONMENU_EXP: ", IMG_CHROME_ADDONMENU_EXP, "\n")
        if random.choice([True]):
            print("REFRESH at closeExpandedChromeAddonMenu ")
            pya.press("f5")
            pya.sleep(3)
            pya.press("esc")
            pya.press("alt")
            pya.keyUp("alt")
        else:
            pya.press("esc")
            pya.press("alt")
            pya.sleep(0.3)
        found = pya.locateOnScreen(IMG_CHROME_ADDONMENU_EXP, confidence=0.7, region=top_row)
        if found:
            print("Detected2 IMG_CHROME_ADDONMENU_EXP: ", IMG_CHROME_ADDONMENU_EXP, "\n")
            print("REFRESH at closeExpandedChromeAddonMenu [2]")
            pya.press("f5")
            pya.sleep(3)
        found = pya.locateOnScreen(IMG_CHROME_ADDONMENU_EXP, confidence=0.7)
        if found:
            print("Detected3 IMG_CHROME_ADDONMENU_EXP: ", IMG_CHROME_ADDONMENU_EXP, "\n")
            print("REFRESH at closeExpandedChromeAddonMenu [3]")
            pya.press("f5")
            pya.sleep(3)
        return pya.locateOnScreen(IMG_CHROME_ADDONMENU_EXP, confidence=0.7) is None
    return False


def webSaveAndOpen(br, delay=0.3, output=None, minimal=False):
    if output is None:
        output = r"C:\temp\borrar_temp.html"
    runSaveWEExtension(delay=delay, output=output, minimal=minimal, removeOthers=True)
    folder = os.path.dirname(output)
    file_regex = os.path.basename(output)
    openLatestWESaved(br, folder=folder, file_regex=file_regex, enable_selection=True)


def runSaveWEExtension(delay=0.3, output=None, minimal=False, removeOthers=True, navigator="Chrome", with_text=""):
    """ Execute Chrome extension to SaveWebElements in a file.
    It needs to has the focus in chrome and the correct tab.

    minimal=True uses SingleHtmlDownloader chrome extension (instead SavePageWE).
            SingleHtmlDownloader must be configured with Shortcut ALT + MAY + A

    removeOthers=True remove all files similar in this folder with digits as wildcard
    """
    print("runSaveWEExte()... ", end="")

    if os.path.isfile(output):
        os.remove(output)

    #### remove
    if removeOthers:
        folder = os.path.dirname(output)
        filename = os.path.basename(output)
        file_regex = re.sub("\d+", "*", filename)
        list_of_files = glob.glob(os.path.join(folder, file_regex)) # * means all if need specific format then *.csv
        for html in list_of_files:
            os.remove(html)

    activateNavigatorWindow(navigator=navigator, with_text=with_text)
    closeExpandedChromeAddonMenu()

    pya.sleep(0.2)
    closeExpandedChromeAddonMenu()
    hold_keys = ["alt"]
    if minimal:
        hold_keys.append("shift")
    with pya.hold(hold_keys):
        pya.sleep(0.2)
        #print(" - Press ALT+a", end="")
        pya.press(['a'])
        print(f"_ zzz {delay}s", end="")
        pya.sleep(max(0.3, delay))
    activateSaveAsWindow() ##Sometimes SaveAs window is not visible...
    found1 = waitUntilLocateImage(IMG_WIN_GUARDAR_TITLE, delay = delay, tries=5, msg="IMG_WIN_GUARDAR_TITLE")
    if closeExpandedChromeAddonMenu():
        return False
    found2 = waitUntilLocateImage(IMG_WIN_GUARDAR_BTN, delay = delay*2, msg="IMG_WIN_GUARDAR_BTN")
    activateSaveAsWindow()
    if found2 and output:
        activateSaveAsWindow()
        pya.write(output)
        pya.sleep(max(0.3, delay))
    if found2:
        with pya.hold('alt'):
            #print(" - Press ALT+g")
            pya.press(['g'])
        closeAnySaveAsDialog()
        return output
    else:
        closeAnySaveAsDialog()
        return False


##########################################
# https://stackoverflow.com/questions/15528939/python-3-timed-input
try:
    from  msvcrt import kbhit, getwche
except ImportError:
    from kbhit import KBHit
    kb = KBHit()
    kbhit = kb.kbhit
    getch = kb.getch

import time
import sys

def pressEnterToContinue():
    input("Press Enter to continue...")


class TimeoutExpired(Exception):
    pass

def input_with_timeout(prompt, timeout, timer=time.monotonic):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if kbhit():
            result.append(getwche()) #XXX can it block on multibyte characters?
            if result[-1] == '\r':
                return ''.join(result[:-1])
        time.sleep(0.04) # just to yield to other processes/threads
    raise TimeoutExpired
##########################################


def stopableSleep(secs=3, countdown=False, silent=False):
    """ Returns False when time expired.
        Returns True when user press Enter

    # TODO countdown
    """
    #print(f"Sleeping {secs:.2f}s...")
    answer = None
    try:
        msg = f"Press ENTER to stop ({secs:.2f}s)"
        if silent:
            msg = ""
        answer = input_with_timeout(msg, secs)
    except TimeoutExpired:
        sys.stdout.write("\033[F") #back to previous line
        sys.stdout.write("\033[K") #clear line  #in console (not in idle or ipython)
        return False
    return True

def openLatestWESaved(br, folder=None, file_regex="*.html", less_x_minutes_ago=60, enable_selection=True):
    """" Open in Selenium last HTML File saved

    less_x_minutes_ago: discard files with timestamp over X minutes ago
    """
    if folder == None:
        forder = DEFAULT_FOLDER

    # Get Last page save
    list_of_files = []
    for i in range(5):
        pya.sleep(i/2+random.random()/3)
        list_of_files = glob.glob(os.path.join(folder, file_regex)) # * means all if need specific format then *.csv
        if len(list_of_files) == 0:
            print(Fore.RED, f"No files '{file_regex}' found at '{folder}' folder. {i+1}/5", Fore.RESET)
        else:
            print(Fore.GREEN, f"Break. {i+1}/5", Fore.RESET)
            break

    if len(list_of_files) == 0:
        print(Fore.RED, f"No files '{file_regex}' found at '{folder}' folder.", Fore.RESET)
        return

    now = dt.utcnow()
    try:
        latest_file = max(list_of_files, key=os.path.getctime)
        file_mtime = dt.utcfromtimestamp(os.path.getmtime(latest_file))
        if (now - file_mtime) > timedelta(minutes=less_x_minutes_ago):
            print(Fore.RED, f"ERROR: lastest_file: {latest_file} . Too old!!!",Fore.RESET, f"(utcnow(): {file_mtime})")
            return
        br.get(latest_file)
    except Exception as e:
        print(e)
        return

    br.execute_script('document.title = "AUTO_SPORTBET - "+document.title')
    try:
        ## Remove favicon to avoid errors locating real bookie webpage
        head = br.find_element_by_tag_name("head")
        link = br.find_element_by_css_selector('link[rel="icon"]')
        br.execute_script('''var link = document.createElement("link");
            link.setAttribute("rel", "icon");
            link.setAttribute("type", "image/png");
            link.setAttribute("href", "https://i.stack.imgur.com/uOtHF.png?s=64&amp;g=1");

            arguments[1].remove();
            arguments[0].appendChild(link);
        ''',head,link)
    except:
        pass

    if enable_selection:
        ### Enablebing select all texts
        ### https://stackoverflow.com/questions/7101982/enabling-blocked-text-selection-using-javascript
        br.execute_script('''
            (function(){
                function allowTextSelection(){
                    window.console&&console.log('allowTextSelection');
                    var style=document.createElement('style');
                    style.type='text/css';
                    style.innerHTML='*,p,div{user-select:text !important;-moz-user-select:text !important;-webkit-user-select:text !important;}';
                    document.head.appendChild(style);
                    var elArray=document.body.getElementsByTagName('*');
                    for(var i=0;i<elArray.length;i++){
                        var el=elArray[i];
                        el.onselectstart=el.ondragstart=el.ondrag=el.oncontextmenu=el.onmousedown=el.onmouseup=function(){return true};
                        if(el instanceof HTMLInputElement&&['text','password','email','number','tel','url'].indexOf(el.type.toLowerCase())>-1){
                            el.removeAttribute('disabled');
                            el.onkeydown=el.onkeyup=function(){return true};
                        }
                    }
                }
                allowTextSelection();
            })();
        ''')


def openLatestDomSaved(folder=None, file_regex="*.html", less_x_minutes_ago=60, enable_selection=True):
    """" Return DOM of the last HTML File saved

    => The same as openLatestWESaved() but without selenium...

    less_x_minutes_ago: discard files with timestamp over X minutes ago
    """
    if folder == None:
        forder = DEFAULT_FOLDER

    # Get Last page save
    list_of_files = []
    for i in range(5):
        pya.sleep(i/2+random.random()/3)
        list_of_files = glob.glob(os.path.join(folder, file_regex)) # * means all if need specific format then *.csv
        if len(list_of_files) == 0:
            print(Fore.RED, f"No files '{file_regex}' found at '{folder}' folder. {i+1}/5", Fore.RESET)
        else:
            print(Fore.GREEN, f"Break. {i+1}/5", Fore.RESET)
            break

    if len(list_of_files) == 0:
        print(Fore.RED, f"No files '{file_regex}' found at '{folder}' folder.", Fore.RESET)
        return

    now = dt.utcnow()
    try:
        latest_file = max(list_of_files, key=os.path.getctime)
        file_mtime = dt.utcfromtimestamp(os.path.getmtime(latest_file))
        if (now - file_mtime) > timedelta(minutes=less_x_minutes_ago):
            print(Fore.RED, f"ERROR: lastest_file: {latest_file} . Too old!!!",Fore.RESET, f"(utcnow(): {file_mtime})")
            return None
        return getDomFromFile(latest_file)
    except Exception as e:
        print(e)
        return None


def getRegionInScreen(num_rows=1, num_cols=1, row=1, col=1, n_x=1, n_y=1, margins=None):
    """
    Divide screen in a matrix of (num_rows, num_cols) in same sizes.
    row = indicates from which row to get
    col = indicates from which column to get
    It returns a box with the the top, left of the row,col cell of this matrix,
        and width = n_x*(cell_width) and height = n_y*(cell_height)

    ### TODO  margin = [left, top, right, bottom ] pixels to sustract of the screen.size
        It helps to removes headers, footers, menus, bars, etc.

    It helps to define a region to get a screenshot or process with OCR.
    IMPORTANT = cells references start at 0 (not at one)

    TODO: Admit row,col with negatives (as python lists)

    Examples:
        getRegionInScreen(num_rows=2, num_cols=2) -> returns first quadrant
        getRegionInScreen(num_rows=1, num_cols=3) -> returns left column
        getRegionInScreen(num_rows=4, num_cols=8, x=4, y=4, n_y=2) -> returns a small central-down region
    """

    width, height = pya.size()

    if margins is not None:
        if len(margins) == 4:
            width -= margins[0] + margins[2] ## left, right
            height -= margins[1] + margins[3] ## left, right
    else:
        margins = [0, 0, 0, 0]

    row = min(row, num_rows-1)
    col = min(col, num_cols-1)

    cell_w = int(width/num_cols)
    cell_h = int(height/num_rows)
    cood_x = margins[0] + (col * cell_w)
    cood_y = margins[1] + (row * cell_h)
    w = n_y * cell_w
    h = n_x * cell_h
    box = (cood_x, cood_y, w, h)

    # if TEST:
    #     print("num_rows, num_cols, row, col, n_x, n_y")
    #     print(num_rows, num_cols, row, col, n_x, n_y)
    #     for i in range(num_rows):
    #         for j in range(num_cols):
    #             cell_w = int(width/num_cols)
    #             cell_h = int(height/num_rows)
    #             print("cell_w:", cell_w)
    #             print("cell_h:", cell_h)
    #             cood_x = j * cell_w
    #             cood_y = i * cell_h
    #             w = n_y * cell_w
    #             h = n_x * cell_h
    #             box = (cood_x, cood_y, w, h)
    #             print(f"row({i}),col({j}): {box}")
    #
    # if TEST:
    #     img = pya.screenshot(region=box)
    #     img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    #     print("Size pantalla:", pya.size())
    #     print("Size after margin:", width, height)
    #     print("Cell size:", cell_w, cell_h)
    #     print("Box:", box)
    #     showImage(img, f"Trozo de pantalla {num_rows}x{num_cols} cell({row},{col})")

    return box

def copy_clipboard():
    pya.hotkey('ctrl', 'c')
    pya.sleep(.05)  # ctrl-c is usually very fast but your program may execute faster
    return pyperclip.paste()

def getElementBoxOnScreen(br, el, top_adjust = 0):
    """ Get Box of screen coordinates of and element of selenium.

        IMPORTANTE: Si se quiere usar para localizar un elemento en Chrome:
            1. **MAXIMIZAR** (antes de guardar, porque puede haber cambios grandes en la estructura de la pÃ¡gina)
            2. Ejecutar webSaveAndOpen(br, output=????)
            3. Obtener el WebElement...  findWithClass(...), p.e.
            4. getElementBoxOnScreen(br, webelement)
            5. moveToH(*xyInsideBox(getElementBoxOnScreen(br, webelement)))

        TODO: Maximize browsers
        TODO: Ensure both has the same scroll position
    """
    from pyscreeze import Box
    # browser_location = driver.get_window_position()
    # # eg: {'y': 127, 'x': 15}
    # # Set the absolute position of your Web element here (top-left corner)
    # element_location = (el.location["x"]+ browser_location["x"],
    #                     el.location["y"]+ browser_location["y"])
    # return element_location
    br.maximize_window()
    y_relative_coord = el.location['y']
    browser_navigation_panel_height = br.execute_script('return window.outerHeight - window.innerHeight;')
    y_absolute_coord = y_relative_coord + browser_navigation_panel_height
    x_absolute_coord = el.location['x']
    box = Box(left= x_absolute_coord,
        top = y_absolute_coord + top_adjust,
        height = el.size["height"],
        width = el.size["width"]
    )
    return box


def getWEwithTexts(elem, texts=["foo","bass"], with_class="ovm-FixtureDetailsWithIndicators_TeamsWrapper"):
    """
    busca webelements que tengan como contenido textual TODOS los textos indicados en 'texts'
    """
    found = []
    elems = elem.find_elements(By.XPATH, f".//*[contains(@class,'{with_class}')]")
    for el in elems:
        texts_found = [False for i in range(len(texts))]
        for line in el.text.split("\n"):
            for i, needle in enumerate(texts):
                if line.find(needle) > -1:
                    texts_found[i] = True
        if all(texts_found):
            found.append(el)
    return found


def _constructClassWithXpath(class_name, tag="*",suffix="", other_condition="", verbose=False):
    if len(suffix) and not suffix.startswith("/"):
        suffix = "/" + suffix
    if len(other_condition) and not (other_condition.startswith("and") or other_condition.startswith("or")):
        print(Fore.RED, f"other_condition [{other_condition}] must start with 'and' or 'or'" )

    xpath = f".//{tag}[contains(@class,'{class_name}') {other_condition}]"+suffix
    if verbose:
        print(xpath)
    return xpath

def _findWithClassSelenium(el, path):
    return el.find_elements(By.XPATH, xpath)


def _findWithClassLxml(dom, xpath):
    return dom.xpath(xpath)


def findWithClass(el, class_name, tag="*",suffix="", other_condition="", verbose=False):
    xpath = _constructClassWithXpath(class_name, tag=tag,suffix=suffix, other_condition=other_condition, verbose=verbose)
    if isinstance(el, WebElement):
        return _findWithClassSelenium(el, xpath)
    elif isinstance(el, etree._Element):
        return _findWithClassLxml(el, xpath)
    else:
        print(Fore.RED, f"ERROR: findWithClass() --  param 'el' is type {type(el)}")
        return None

def weText(el):
    if isinstance(el, WebElement):
        return el.text
    elif isinstance(el, etree._Element):
        return '\n'.join(el.itertext())


def getDomFromFile(filename):
    ## Wait a little if is not written already
    if filename == False or str(filename) == 'False':
        print(Fore.RED, f"getDomFromFile -- File '{filename}'??", Fore.RESET)
        return None
    for i in range(5):
        pya.sleep(0.2)
        if not os.path.exists(filename):
            print(Fore.RED, f"getDomFromFile -- No file '{filename}' found. {i+1}/5", Fore.RESET)
        else:
            print(Fore.GREEN, f"getDomFromFile -- File '{filename}' found. {i+1}/5", Fore.RESET)
            break
    dom = None
    with open(filename,'r', encoding='utf-8') as f:
        html = f.read()
        dom = etree.HTML(html)
    return dom


######################################
def startChronometer(text=""):
    """Para medir el tiempo que tarda algo"""
    init_time = time.time()
    return init_time, text

def stopChronometer(chronometer, console=True):
    """Para medir el tiempo que tarda algo. """
    now = time.time()
    init_time = chronometer[0]
    text = chronometer[1]
    diff_time = round(now - init_time, 2)
    if console or text != "":
        print(f"{text}: It took", diff_time, "seconds")
    return diff_time
######################################


try:
    import winsound
except ImportError:
    def playsound(frequency=400,duration=0.5):
        #apt-get install beep
        os.system('beep -f %s -l %s' % (frequency,duration))
else:
    def playsound(frequency=400,duration=0.5):
        #winsound.Beep(frequency,duration)
        winsound.MessageBeep(10)


def confirm_dialog(text, title, answer, buttons=['OK', 'Cancel']):
    answer[0] = pya.confirm(text=text, title=title, buttons=buttons)
    return answer


def threadConfirmDialog(msg="Hello world", title="Title hello world", answer=[False]):
    t = Thread(target=confirm_dialog, args = [msg, title, answer])
    t.daemon = True
    t.start()

    print(f"Confirm answer??? [{answer}]") ###Pero tras aceptar o cancelar answer tendrÃ¡ el resultado
    return t
    ## Por si se quiere usar para confirmar una apuesta!!