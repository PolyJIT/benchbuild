#!/usr/bin/awk -f
BEGIN { FS=","; OFS=","; }

(FNR > 1) {
	stdCov[$1] = $4;
	dynCov[$1] = $14;
	caddyCov[$1] = $24;
	
	stdPapiTime[$1] = $5;
	dynPapiTime[$1] = $15;
	caddyPapiTime[$1] = $25;

	stdTime[$1]= $6;
	dynTime[$1]= $16;
	caddyTime[$1]= $26;
	
	stdCalls[$1] = $10;
	dynCalls[$1] = $20;
	caddyCalls[$1] = $30;
}

END {
	printf "%s, %s, %s, %s, %s, %s\n",
		"Name", "Class", "ExecCov", "Time", "PapiTime", "Calls";

	for (p in stdCov) {
		printf "%s, %s, %s, %s, %s, %s\n",
			p, "Static", stdCov[p], stdTime[p], stdPapiTime[p], stdCalls[p];

		printf "%s, %s, %s, %s, %s, %s\n",
		    p, "Algebraic", caddyCov[p], caddyTime[p], caddyPapiTime[p], caddyCalls[p];

		printf "%s, %s, %s, %s, %s, %s\n",
			p, "Dynamic" , dynCov[p], dynTime[p], dynPapiTime[p], dynCalls[p];
		
		#printf "%s, %s, %s, %s, %s, %s\n",
		#	p, "Raw"     , "0", rawTime[p], "0", "0";
	}
}