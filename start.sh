# fresh compile at startup
ls -al > log.txt
pushd ./vue-cutter
npm install
npm run justbuild
popd
export PRODUCTION="1"
python -OO worker.py & 
python -OO app.py
