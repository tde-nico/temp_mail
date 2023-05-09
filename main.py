import pyperclip
import requests
from random import choice
import string
from time import sleep
import sys
from re import search
import os

API = 'https://www.1secmail.com/api/v1/'





def generate_user_name():
	name = string.ascii_lowercase + string.digits
	username = ''.join(choice(name) for char in range(10))
	return username


def create_mail(new_mail):
	user = search(r'login=(.*)&', new_mail).group(1)
	domain = search(r'domain=(.*)', new_mail).group(1)
	mail = f"{user}@{domain}"
	return mail


def delete_mail(mail):
	url = 'https://www.1secmail.com/mailbox'
	login, domain = mail.split('@', 1)
	data = {
		'action': 'deleteMailbox',
		'login': f'{login}',
		'domain': f'{domain}'
	}
	req = requests.post(url, data=data)


def print_statusline(msg: str):
	last_msg_length = len(print_statusline.last_msg) if hasattr(print_statusline, 'last_msg') else 0
	print(' ' * last_msg_length, end='\r')
	print(msg, end='\r')
	sys.stdout.flush()
	print_statusline.last_msg = msg


def mkdir(folder):
	cwd = os.getcwd()
	new_dir = os.path.join(cwd, folder)
	if not os.path.exists(new_dir):
		os.makedirs(new_dir)
	return new_dir


def read_mail(login, domain, mail_id):
	msg_read = f'{API}?action=readMessage&login={login}&domain={domain}&id={mail_id}'
	req = requests.get(msg_read).json()
	content = dict(req.items())
	content['id'] = mail_id
	return content


def write_mail(content, mail_dir, mail):
	mail_id = content.get('id')
	mail_file_path = os.path.join(mail_dir, f'{mail_id}.txt')

	with open(mail_file_path,'w') as file:
		file.write(f"To: {mail}\n\n")
		for key, text in content.items():
			file.write(f"{key}: {text}\n")


def check_mails(mail):
	login, domain = mail.split('@', 1)

	request_link = f'{API}?action=getMessages&login={login}&domain={domain}'
	req = requests.get(request_link).json()
	length = len(req)

	if length == 0:
		print_statusline("[-] Your mailbox is empty")
		return

	mail_ids = []
	for responce in req:
		for key, mail_id in responce.items():
			if key == 'id':
				mail_ids.append(mail_id)

	print(f"[+] You received {length}", 'mails' if length > 1 else 'mail')

	mail_dir = mkdir('Mails')

	for mail_id in mail_ids:
		content = read_mail(login, domain, mail_id)
		write_mail(content, mail_dir, mail)




def main():
	domainList = ['1secmail.com', '1secmail.net', '1secmail.org']
	rand_domain = choice(domainList)
	custom_name = ''
	try:

		if custom_name:
			new_mail = f"{API}?login={custom_name}&domain={rand_domain}"
		else:
			new_mail = f"{API}?login={generate_user_name()}&domain={rand_domain}"
		request_mail = requests.get(new_mail)
		mail = create_mail(new_mail)
		pyperclip.copy(mail)
		print(f"[+] {mail} Created (Email address copied to clipboard.)")
		while True:
			check_mails(mail)
			sleep(5)

	except KeyboardInterrupt:
		delete_mail(mail)
		os.system('cls' if os.name == 'nt' else 'clear')
		print(f'[+] {mail} Deleted')


if __name__ == '__main__':
	main()
