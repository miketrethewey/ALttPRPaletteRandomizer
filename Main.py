import random
import logging
import time
import argparse
import os

__version__ = "0.1-dev"

#Usage: python Main.py --rom lttpromtobepatched.sfc
#generates lttpromtobepatched_edit_[time].sfc
#General rom patching copied from https://github.com/LLCoolDave/ALttPEntranceRandomizer

def write_byte(rom, address, value):
	if value == '' or value == '0':
		value = '00'
	rom[address] = int(value,16)
	logger.info('0x' + hex(address)[2:].upper() + ': ' + value)

def write_bytes(rom, startaddress, values):
	for i, value in enumerate(values):
		write_byte(rom, startaddress + i, value)

def clamp(val, minimum=0, maximum=255):
	if val < minimum:
		return minimum
	if val > maximum:
		return maximum
	return int(val)

def colorscale(hexstr, scalefactor):
	hexstr = hexstr.strip('#')
	
	if scalefactor < 0 or len(hexstr) != 6:
		return hexstr
	
	r,g,b = int(hexstr[:2], 16), int(hexstr[2:4], 16), int(hexstr[4:], 16)
	
	r = clamp(r * scalefactor)
	g = clamp(g * scalefactor)
	b = clamp(b * scalefactor)
	
	return "%02x%02x%02x".upper() % (r,g,b)

def randomcolor():
	r,g,b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
	return "%02x%02x%02x".upper() % (r,g,b)

def hex2snes(hex):
	hex = hex.strip('#')
	r,g,b = int(hex[:2],16), int(hex[2:4],16), int(hex[4:],16)
	s = ( ((int( b / 8) << 10) | (int( g / 8) << 5) | (int( r / 8) << 0)) )
	s = "%02x" % s
	s = s.upper()
	
	return [s[2:],s[:2]]

def darken(hex):
	return colorscale(hex,.8)

def lighten(hex):
	return colorscale(hex,1.2)

def adjust(hex,mode):
	if mode == "darken":
		hex = darken(hex)
	elif mode == "lighten":
		hex = lighten(hex)

	return hex

if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--loglevel',	default='info',	const='info',	nargs='?',	choices=['error', 'info', 'warning', 'debug'],	help='Select level of logging for output.')
	parser.add_argument('--rom',		help='Path to a lttp rom to be patched.')
	parser.add_argument('--lthat',		default='None',	help='Light Color for Hat,   in Hex format: 000000')
	parser.add_argument('--dkhat',		default='None',	help='Dark  Color for Hat,   in Hex format: 000000')
	parser.add_argument('--lttunic',	default='None',	help='Light Color for Tunic, in Hex format: 000000')
	parser.add_argument('--dktunic',	default='None',	help='Dark  Color for Tunic, in Hex format: 000000')
	parser.add_argument('--sleeves',	default='None',	help='Sleeve Color,          in Hex format: 000000')
	parser.add_argument('--randomhat',	default='no',	help='Randomize Hat Color')
	parser.add_argument('--randomtunic',	default='no',	help='Randomize Tunic Color')
	parser.add_argument('--randomsleeves',	default='no',	help='Randomize Sleeve Color')
	parser.add_argument('--randomoutfit',	default='no',	help='Randomize Outfit Color')
	args = parser.parse_args()
	
	if args.rom is None:
		input('No rom specified. Please run with -h to see help for further information. \nPress Enter to exit.')
		exit(1)
	if not os.path.isfile(args.rom):
		input('Could not find valid rom for patching at path %s. Please run with -h to see help for further information. \nPress Enter to exit.' % args.rom)
		exit(1)
	
	#set up logger
	loglevel = {'error': logging.ERROR, 'info': logging.INFO, 'warning': logging.WARNING, 'debug': logging.DEBUG}[args.loglevel]
	logging.basicConfig(format='%(message)s', level=loglevel)
	
	logger = logging.getLogger('')
	
	logger.info('Patching ROM.')
	
	rom = bytearray(open(args.rom, 'rb').read())
	
	lthat = args.lthat
	dkhat = args.dkhat
	lttunic = args.lttunic
	dktunic = args.dktunic
	sleeves = args.sleeves
	
	gmailbyte   = 0x0DD308
	dktunicbyte = gmailbyte + 8 * 2
	lttunicbyte = dktunicbyte + 2
	dkhatbyte   = lttunicbyte + 2
	lthatbyte   = dkhatbyte + 2
	sleevesbyte = lthatbyte + 4
	
	if args.randomhat != "no":
		logger.info('Randomize Hat!')
		dkhat = randomcolor()
	if args.randomtunic != "no":
		logger.info('Randomize Tunic!')
		dktunic = randomcolor()
	if args.randomoutfit != "no":
		logger.info('Randomize Outfit!')
		dktunic = randomcolor()
		dkhat = randomcolor()
		sleeves = randomcolor()
	
	# DkTunic is defined
	if dktunic != "None":
		byte = dktunicbyte
		value = hex2snes(dktunic)
		write_bytes(rom,byte,value)
		# LtTunic is defined
		if lttunic != "None":
			byte = lttunicbyte
			value = hex2snes(lttunic)
			write_bytes(rom,byte,value)
		else:
		# LtTunic is not defined, make it
			lttunic = adjust(dktunic,"lighten")
			byte = lttunicbyte
			value = hex2snes(lttunic)
			write_bytes(rom,byte,value)

	# DkTunic is not defined
	# LtTunic is defined
	elif lttunic != "None":
		# Write LtTunic, make DkTunic
		byte = lttunicbyte
		value = hex2snes(lttunic)
		write_bytes(rom,byte,value)
		dktunic = adjust(lttunic,"darken")
		byte = dktunicbyte
		value = hex2snes(dktunic)
		write_bytes(rom,byte,value)
	
	# DkHat is defined
	if dkhat != "None":
		byte = dkhatbyte
		value = hex2snes(dkhat)
		write_bytes(rom,byte,value)
		# LtHat is defined
		if lthat != "None":
			byte = lthatbyte
			value = hex2snes(lthat)
			write_bytes(rom,byte,value)
		else:
		# LtHat is not defined, make it
			lthat = adjust(dkhat,"lighten")
			byte = lthatbyte
			value = hex2snes(lthat)
			write_bytes(rom,byte,value)

	# DkHat is not defined
	# LtHat is defined
	elif lthat != "None":
		# Write LtHat, make DkHat
		byte = lthatbyte
		value = hex2snes(lthat)
		write_bytes(rom,byte,value)
		dkhat = adjust(lthat,"darken")
		byte = dkhatbyte
		value = hex2snes(dkhat)
		write_bytes(rom,byte,value)

	if sleeves == "None":
		sleeves = adjust(dktunic,"darken")

	byte = sleevesbyte
	value = hex2snes(sleeves)
	write_bytes(rom,byte,value)

	if args.randomhat != "no":
		logger.info('Random Hat: ' + dkhat + '/' + lthat)
	if args.randomtunic != "no":
		logger.info('Random Tunic: ' + dktunic + '/' + lttunic)
	if args.randomoutfit != "no":
		logger.info('Random Outfit:')
		logger.info('Random Tunic: ' + dktunic + '/' + lttunic)
		logger.info('Random Hat: ' + dkhat + '/' + lthat)
		logger.info('Random Sleeves: ' + sleeves)
	
	outfilename = '%s' % (os.path.basename(args.rom).replace(".sfc","") + "_edit_" + str(int(time.time())) + ".sfc")
	logger.info("Output to: " + outfilename)
	
	with open('%s' % outfilename, 'wb') as outfile:
		outfile.write(rom)
	
	logger.info('Done.')
