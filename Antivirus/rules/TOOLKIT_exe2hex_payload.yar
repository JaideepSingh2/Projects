/*
    This Yara ruleset is under the GNU-GPLv2 license (http://www.gnu.org/licenses/gpl-2.0.html) and open to any user or organization, as    long as you use it under this license.

*/

/*
	Yara Rule Set
	Author: Florian Roth
	Date: 2016-01-15
	Identifier: Exe2hex
*/

rule Payload_Exe2Hex : toolkit {
	meta:
		description = "Detects payload generated by exe2hex"
		author = "Florian Roth"
		reference = "https://github.com/g0tmi1k/exe2hex"
		date = "2016-01-15"
		score = 70
	strings:
		$a1 = "set /p \"=4d5a" ascii
		$a2 = "powershell -Command \"$hex=" ascii
		$b1 = "set+%2Fp+%22%3D4d5" ascii
		$b2 = "powershell+-Command+%22%24hex" ascii
		$c1 = "echo 4d 5a " ascii
		$c2 = "echo r cx >>" ascii
		$d1 = "echo+4d+5a+" ascii
		$d2 = "echo+r+cx+%3E%3E" ascii
	condition:
		all of ($a*) or all of ($b*) or all of ($c*) or all of ($d*)
}
