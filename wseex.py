import requests,re
import sys
from requests.exceptions import ReadTimeout, Timeout, ConnectionError,ChunkedEncodingError,TooManyRedirects
from urllib3.exceptions import ProtocolError,InvalidChunkLength
import os, fnmatch; os.system("clear")
import csv
from collections import defaultdict, Counter
from os.path import abspath, dirname
from multiprocessing import Process, cpu_count, Manager
from time import sleep

class colors:
	RED = '\033[31m'
	ENDC = '\033[m'
	GREEN = '\033[32m'
	YELLOW = '\033[33m'
	BLUE = '\033[34m'
	RED_BG = '\033[41m\033[1m'
	GREEN_BG = '\033[42m'

class inf:
	expected_response = 101
	control_domain = 'd22236fd6eam5f.cloudfront.net'
	payloads = { "Host": control_domain, "Upgrade": "websocket", "DNT":  "1", "Accept-Language": "*", "Accept": "*/*", "Accept-Encoding": "*", "Connection": "keep-alive, upgrade", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36" }
	file_hosts = ""
	result_success = []
	columns = defaultdict(list)
	txtfiles= []
	hostpath = 'host'

def text():
	global domainlist
	num_file=1
	files = os.listdir(inf.hostpath)
	print(" [" + colors.RED_BG + " Files Found " + colors.ENDC + "] ")
	for f in files:
		if fnmatch.fnmatch(f, '*.txt'):
			print( str(num_file),str(f))
			num_file=num_file+1
			inf.txtfiles.append(str(f))

	print("")
	print(" M back to Menu ")
	fileselector = input(" Choose Target Files : ")
	if fileselector.isdigit():
		print("")
		print(" Target Chosen : " + colors.RED_BG + " "+inf.txtfiles[int(fileselector)-1]+" "+colors.ENDC)
		file_hosts = str(inf.hostpath) +"/"+ str(inf.txtfiles[int(fileselector)-1])
	else:
		menu()

	with open(file_hosts) as f:
		parseddom = f.read().split()

	domainlist = list(set(parseddom))
	domainlist = list(filter(None, parseddom))

	print(" Total of Domains Loaded: " + colors.RED_BG + " " +str(len(domainlist)) + " "+colors.ENDC )
	print("")

	with Manager() as manager:
		num_cpus = cpu_count()
		processes = []
		R = manager.list()
		for process_num in range(num_cpus):
			section = domainlist[process_num::num_cpus]
			p = Process(target=engine, args=(section,R,))
			p.start()
			processes.append(p)
		for p in processes:
			p.join()
		R = list(R)

		print("")
		print(" Total of Domains Queried : "  + colors.RED_BG + " "+str(len(R)) +" "+ colors.ENDC )
		if len(inf.result_success) >= 0:
			print(" Successfull Result : " + colors.GREEN_BG + " "+str(len(R))+ " "+colors.ENDC)
	print(R)

	print("")
	print("Scanning Finished!")
	print("1. Go Back to Menu")
	print("2. Scanning Again")
	print("3. Quit Instead")
	print("")
	ans=input("Choose Option: ")
	if ans=="2":
		text()
	elif ans=="3":
		exit()
	else:
		menu()

def csv():
	global domainlist
	num_file=1
	files = os.listdir(inf.hostpath)
	print(" [" + colors.RED_BG + " Files Found " + colors.ENDC + "] ")
	for f in files:
		if fnmatch.fnmatch(f, '*.csv'):
			print( str(num_file),str(f))
			num_file=num_file+1
			inf.txtfiles.append(str(f))

	print("")
	print(" M back to Menu ")
	fileselector = input(" Choose Target Files : ")
	if fileselector.isdigit():
		print("")
		print(" Target Chosen : " + colors.RED_BG + " "+inf.txtfiles[int(fileselector)-1]+" "+colors.ENDC)
		file_hosts = str(inf.hostpath) +"/"+ str(inf.txtfiles[int(fileselector)-1])
	else:
		menu()

	with open(file_hosts,'r') as csv_file:
		reader = csv.reader(csv_file)

		for row in reader:
			for (i,v) in enumerate(row):
				inf.columns[i].append(v)
	parseddom=inf.columns[9]+inf.columns[3]
	domainlist = list(set(parseddom))
	domainlist = list(filter(None, parseddom))

	print(" Total of Domains Loaded: " + colors.RED_BG + " " +str(len(domainlist)) + " "+colors.ENDC )
	print("")

	with Manager() as manager:
		num_cpus = cpu_count()
		processes = []
		R = manager.list()
		for process_num in range(num_cpus):
			section = domainlist[process_num::num_cpus]
			p = Process(target=engine, args=(section,R,))
			p.start()
			processes.append(p)
		for p in processes:
			p.join()

		print("")
		print(" Total of Domains Queried : "  + colors.RED_BG + " "+str(len(inf.result_success)) +" "+ colors.ENDC)
		if len(result_success) >= 0:
			print(" Successfull Result : " + colors.GREEN_BG + " "+str(len(inf.result_success))+ " "+colors.ENDC)

	print("")
	print("Scanning Finished!")
	print("1. Go Back to Menu")
	print("2. Scanning Again")
	print("3. Quit Instead")
	print("")
	ans=input("Choose Option: ")
	if ans=="2":
		fileselector=""
		csv()
	elif ans=="3":
		exit()
	else:
		fileselector=""
		menu()

def enum():
	subd = input("\nInput Domain: ")
	subd = subd.replace("https://","").replace("http://","")
	r = requests.get("https://api.hackertarget.com/hostsearch/?q=" + subd, allow_redirects=False)
	yn = input("\nContinue Scanning? (y/n): ")
	if yn.lower() == "y":
		head = { "Host": frontdom, "Upgrade": "websocket", "DNT":  "1", "Accept-Language": "*", "Accept": "*/*", "Accept-Encoding": "*", "Connection": "keep-alive, upgrade", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36" }
		sukses = []
		if r.text == "error invalid host":
			exit("ERR: error invalid host")
		else:
			print("\nScanning Started... CTRL + Z to Exit!")
			subdo = re.findall("(.*?),",r.text)
			for sub in subdo:
				try:
					req = requests.get(f"http://{sub}",headers=head,timeout=0.7,allow_redirects=False)
					if req.status_code == 101:
						print(" ["+colors.GREEN_BG+" HIT "+colors.ENDC+"] " + str(sub))
						sukses.append(str(sub))
					else:
						print(" ["+colors.RED_BG+ " FAIL " + colors.ENDC + "] " + sub + " [" +colors.RED_BG + " "+str(req.status_code)+" "+colors.ENDC+"]")
				except (Timeout, ReadTimeout, ConnectionError):
					print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + sub +" [" +colors.RED_BG+" TIMEOUT "+colors.ENDC+"]")
				except(ChunkedEncodingError, ProtocolError, InvalidChunkLength):
					print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " +sub +" [" +colors.RED_BG+" Invalid Length "+colors.ENDC+"]")
					pass
				except(TooManyRedirects):
					print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + sub + " [" +colors.RED_BG+" Redirects Loop "+colors.ENDC+"]")
					pass
				except:
					pass
			print(" Loaded: " + colors.GREEN + str(len(sub)) + colors.ENDC)
			print("Successfull Result: \n")
			for res in sukses:
				print(res)
			input("Continue...")
			menu()
	else:
		menu()

def wsocket():
	global headers,domainlist
	wsocket = { "Connection": "Upgrade", "Sec-Websocket-Key": "dXP3jD9Ipw0B2EmWrMDTEw==", "Sec-Websocket-Version": "13", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36", "Upgrade": "websocket" }
	frontdom = wsocket
	num_file=1

	files = os.listdir(inf.hostpath)
	print(" [" + colors.RED_BG + " Files Found " + colors.ENDC + "] ")
	for f in files:
		if fnmatch.fnmatch(f, '*.txt'):
			print( str(num_file),str(f))
			num_file=num_file+1
			inf.txtfiles.append(str(f))

	print("")
	print(" M back to Menu ")
	fileselector = input(" Choose Target Files : ")
	if fileselector.isdigit():
		print("")
		print(" Target Chosen : " + colors.RED_BG + " "+inf.txtfiles[int(fileselector)-1]+" "+colors.ENDC)
		file_hosts = str(inf.hostpath) +"/"+ str(inf.txtfiles[int(fileselector)-1])
	else:
		menu()

	with open(file_hosts) as f:
		parseddom = f.read().split()

	domainlist = list(set(parseddom))
	domainlist = list(filter(None, parseddom))

	print(" Total of Domains Loaded: " + colors.RED_BG + " " +str(len(domainlist)) + " "+colors.ENDC )
	print("")

	with Manager() as manager:
		num_cpus = cpu_count()
		processes = []
		R = manager.list()
		for process_num in range(num_cpus):
			section = domainlist[process_num::num_cpus]
			p = Process(target=engine, args=(section,R,))
			p.start()
			processes.append(p)
		for p in processes:
			p.join()

		print("")
		print(" Total of Domains Queried : "  + colors.RED_BG + " "+str(len(inf.result_success)) +" "+ colors.ENDC)
		if len(inf.result_success) >= 0:
			print(" Successfull Result : " + colors.GREEN_BG + " "+str(len(inf.result_success))+ " "+colors.ENDC)

	print("")
	print("Scanning Finished!")
	print("1. Go Back to Menu")
	print("2. Scanning Again")
	print("3. Quit Instead")
	print("")
	ans=input("Choose Option: ")
	if ans=="2":
		wsocket()
	elif ans=="3":
		exit()
	else:
		menu()

def engine(domainlist,R):
	for domain in domainlist:
		try:
			r = requests.get("http://" + domain, headers=headers, timeout=0.7, allow_redirects=False)
			if r.status_code == inf.expected_response:
				print(" ["+colors.GREEN_BG+" HIT "+colors.ENDC+"] " + domain)
				print(domain, file=open("RelateCFront.txt", "a"))
				R.append(str(domain))
			elif r.status_code != inf.expected_response:
				print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + domain + " [" +colors.RED_BG+" " + str(r.status_code) + " "+colors.ENDC+"]")
		except (Timeout, ReadTimeout, ConnectionError):
			print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + domain + " [" + colors.RED_BG +" TIMEOUT "+colors.ENDC+"]")
		except(ChunkedEncodingError, ProtocolError, InvalidChunkLength):
			print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + domain + " [" + colors.RED_BG+" Invalid Length "+colors.ENDC + "]")
			pass
		except(TooManyRedirects):
			print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + domain + " [" +colors.RED_BG+" Redirects Loop "+colors.ENDC+"]")
		except:
			pass

def menu():
	print('''

__  _  ________ ____   ____  
\ \/ \/ /  ___// __ \_/ __ \ 
 \     /\___ \\  ___/\  ___/ 
  \/\_//____  >\___  >\___  >
			\/     \/     \/  

	''')
	print("    [" + colors.RED_BG + " Domain : Fronting " + colors.ENDC + "]")
	print("     ["+colors.RED_BG+" Author " + colors.ENDC + ":" + colors.GREEN_BG + " Kiynox " + colors.ENDC + "]")
	print("")

	print("1. CDN Websocket")
	print("2. Local Websocket")
	print("q to Quit")
	print("")
	opsi=input(" Choose Option :  ")
	print("")
	if str(opsi)=="1":
		global frontdom
		global headers
		print("Put Your Target Domain Front")
		print("y to leave it as Default (Class)")
		print("q to Quit")
		print("")
		frontdom=input(" Domain : ")
		if str(frontdom)=="y":
			headers = inf.payloads
			CDNer()
		elif str(frontdom)=="q":
			exit()
		else:
			headers = { "Host": frontdom, "Upgrade": "websocket", "DNT":  "1", "Accept-Language": "*", "Accept": "*/*", "Accept-Encoding": "*", "Connection": "keep-alive, upgrade", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36" }
			print("")
			print(colors.RED_BG + " Warning! " + colors.ENDC + " : " + colors.RED_BG+ " INVALID " + colors.ENDC + " Domain will interrupt the script! Make sure to input " + colors.GREEN_BG + " VALID "+ colors.ENDC + " Domain!")
			CDNer()
	elif str(opsi)=="2":
		wsocket()
	else:
		exit()
	
def CDNer():
	print("1. Scanning File List from .txt")
	print("2. Scanning File List from .csv")
	print("3. Scanning from Subdomain Enum [HackerTarget]")
	print("4. Local Websocket Finder")
	print("m to Menu")
	print("q to Quit")
	print("")
	opsi=input(" Choose Option :  ")
	print("")
	if str(opsi)=="1":
		text()
	elif str(opsi)=="2":
		csv()
	elif str(opsi)=="3":
		global frontdom
		enum()
	elif str(opsi)=="4":
		wsocket()
	elif str(opsi)=="m":
		menu()
	else:
		exit()

os.chdir(dirname(abspath(__file__)))
if not os.path.exists(inf.hostpath):
	os.makedirs(inf.hostpath)
menu()