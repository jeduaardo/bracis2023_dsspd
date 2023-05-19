# bracis2023_dsspd

Requirements:

Python requirements can be found at cgp-grn/source/requirements. Script getRequirements.sh should automatically install the dependencies.
OpenCL >= 1.2


Usage for reproducing the presented results

python CGPGRN.py -e ExpressionData.csv -p Pseudotime.csv -pn ProblemName -s Suffix -d Discretization -r nIndependentRuns -cgpn nCGPNodes -cgpg nCGPGenerations -fullTT -run

e.g.: python CGPGRN.py -e ExpressionData.csv -p Pseudotime.csv -pn mCAD -s 2000-0 -d DSSPD -r 5 -cgpn 500 -cgpg 50000 -fullTT -run
