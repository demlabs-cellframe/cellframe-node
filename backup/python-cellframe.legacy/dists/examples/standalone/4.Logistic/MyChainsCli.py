import sys
import CellFrame.AppCli

app_name=’MyChains’
tmp_dir = os.getcwd() + "/tmp"
var_dir = os.getcwd() + "/var"
sys.exit( AppCli.main(app_name,tmp_dir+’/node_cli’, sys.argv ))
