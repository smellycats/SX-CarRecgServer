from car_recg import app
from car_recg.recg_ser import RecgServer
from ini_conf import MyIni

if __name__ == '__main__':
    rs = RecgServer()
    rs.main()
    my_ini = MyIni()
    sys_ini = my_ini.get_sys_conf()
    app.config['THREADS'] = sys_ini['threads']
    app.config['MAXSIZE'] = sys_ini['threads'] * 16
    app.run(host='0.0.0.0', port=sys_ini['port'], threaded=True)
    del rs
    del my_ini
