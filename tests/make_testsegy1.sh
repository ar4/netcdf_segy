#!/bin/sh

python make_testbin1.py
suaddhead < testbin1.bin ns=20 | sushw key=dt,fldr,gx,scalco a=1234,777,456789,-1000 b=0,0,1000,0 c=0,1,0,0 j=ULONG_MAX,10,10,ULONG_MAX > testsegy1.su
segyhdrs < testsegy1.su
segywrite < testsegy1.su tape=testsegy1.segy
