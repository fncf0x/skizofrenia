# skizofrenia
Skizofrenia is an easy to use proxy provider with the possibility to chose a region.
## How it work
Skizofrenia has two main running services:

- **JProxy**: A daemon that permanently runs spiders in multi-thread configured on the *config.yaml* file, with a wait delay between each run, and a priority. And store each proxy with the correct region in a DB.
- **webservice**: An API that fetch either a random or based on a provided region proxy from the DB.

![](Skizofrenia.png?raw=true)

## How to deploy
clone the repo
```bash
git clone https://github.com/mps-dz/skizofrenia
```
change working directory
```bash
cd skizofrenia/
```
#### Jproxy
prepare Python3.8 environment
```bash
cd jproxy/
python3.8 -m venv env
source env/bin/activate
pip install --upgrade pip
```
install requirements
```bash
pip install -r requirements.txt
```
export env variables
```bash
export PROXY_SRC='./proxy_sources'
export PROXY_DB_URI='../database/jproxy.db'
export PROXY_CONFIG_FILE='./config.yaml'
```
run in a tmux session
```bash
deactivate
tmux new -s jproxy
source env/bin/activate
python jproxy.py
```
#### webservice
prepare Python3.8 environment
```bash
cd webservice/
python3.8 -m venv env
source env/bin/activate
pip install --upgrade pip
```
install requirements
```bash
pip install -r requirements.txt
```
export env variables
```bash
export PROXY_DB_URI='../database/jproxy.db'
```
run in a tmux session
```bash
deactivate
tmux new -s skizofrenia
source env/bin/activate
python api.py
```
## Add a new proxy src
In case you want to add a new proxy source, follow the steps:

- add your spider in the *jproxy/proxy_sources* directory

*the spider should check the proxies, and the stdout should be dumped when the program exit. See other spiders as an exemple*

- update the *config.yaml* file

*Add name (source name), path (program file name), wait_delay (time to wait between each run*
```yaml
- name: Spys
...[snip]
- name: Test
  check_delay: 15 # each 50s
  path: test.py
  prior: 1 # not important yet
EOF
```