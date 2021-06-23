import sqlite3
import os
import pandas as pd
import shutil
import json
import numpy as np
import zipfile

''' 
Database class with functions:
    a) create:
        - new project:
            ^ project file !!!!!!!!!!!!!!!!
            ^ project setting !!!!!!!!!!!!!
        - database:
            ^ projects
            ^ existing control network
            ^ dump file
            ^ new control network
            ^ dat files directories
        - temporary txt files:
            ^ existing control network
            ^ dump file
            ^ new control network
            ^ steps
            ^ new points
            ^ changed points
            ^ dat file
        - txt files:
            ^ dat file
    b) import:
        - existing control network
        - dump file from StarNet
        - old points !!!!!!!!!!!!!!!!!!!!!!
        - old residuals !!!!!!!!!!!!!!!!!!!
        - dat file !!!!!!!!!!!!!!!!!!!!!!!!
        - data from old project/revision: !!!!
            ^
    c) export: 
        - new control network !!!!!!!!!!!!!
        - report csv !!!!!!!!!!!!!!!!!!!!!!
        - changed points !!!!!!!!!!!!!!!!!!
        - new points !!!!!!!!!!!!!!!!!!!!!!
        - old points !!!!!!!!!!!!!!!!!!!!!!
    d) update file: !!!!!!!!!!!!!!!!!!!!!!!
        - database:  
            ^ existing control network
                * change name for old point
                * remove point
            ^ dump file
            ^ new control network
        - temporary txt files:
            ^ existing control network
            ^ dump file
            ^ new control network
            ^ steps
            ^ new points
            ^ changed points
    e) delate:
        - project
        - point !!!!!!!!!!!!!!!!!!!!!!!!!
        
'''


class CTNdb(object):

    def __init__(self,
                 ctn_data_id='./CTN_data',
                 dump_db_id='CTN_db_dump.db', exist_db_id='CTN_db_ex.db', new_db_id='CTN_db_new.db',
                 proj_db_id='CTN_db_proj.db', dat_db_id='CTN_db_dat.db', res_db_id='CTN_db_res.db',
                 ch_db_id='CTN_db_ch.db',
                 dump_tb_id='CTN_dump', exist_tb_id='CTN_ex_pt', new_tb_id='CTN_new_pt', dat_tb_id='CTN_dat_f',
                 proj_tb_id='CTN_projects', dat_res_tb_id='CTN_dat_res', dat_del_tb_id='CTN_dat_del',
                 res_tb_id='CTN_residua', ch_tb_id='CTN_change_pt',
                 proj_tp='project', dat_tp='dat_file', dp_tp='dump_file', ex_tp='existing_points',
                 new_tp='new_points', res_tp='resection_points', del_tp='delete_points', ch_tp='change_points',
                 residua_tp='residuals',
                 res_points='#res', del_points='#del',
                 temp_folder='/temp', dat_folder='/dat_files',
                 proj_file='_proj.json', current_file_proj='./temp/current_proj.json',
                 old_file_proj='./temp/old_proj.json',
                 temp_ex_file='/CTN_temp_ex.json', temp_new_file='/CTN_temp_new.json',
                 temp_new_p_file='/CTN_temp_new_points.json', temp_change_p_file='/CTN_temp_change_points.json',
                 temp_dump_file='/CTN_temp_dump.json', temp_steps_file='/CTN_temp_steps.json',
                 temp_new_out_file='/CTN_temp_new_points_out.json',
                 temp_chg_out_file='/CTN_temp_changed_points_out.json',
                 temp_dat_file='/CTN_temp_dat.json', temp_residuals='/CTN_temp_residua.json',
                 temp_compare='/CTN_temp_comparison.json'):

        self.ctn_data_id = ctn_data_id

        self.dump_db_id = dump_db_id
        self.exist_db_id = exist_db_id
        self.proj_db_id = proj_db_id
        self.new_db_id = new_db_id
        self.dat_db_id = dat_db_id
        self.res_db_id = res_db_id
        self.ch_db_id = ch_db_id

        self.dump_tb_id = dump_tb_id
        self.exist_tb_id = exist_tb_id
        self.new_tb_id = new_tb_id
        self.ch_tb_id = ch_tb_id
        self.dat_tb_id = dat_tb_id
        self.proj_tb_id = proj_tb_id
        self.dat_res_tb_id = dat_res_tb_id
        self.dat_del_tb_id = dat_del_tb_id
        self.res_tb_id = res_tb_id

        self.proj_tp = proj_tp
        self.dat_tp = dat_tp
        self.dp_tp = dp_tp
        self.ex_tp = ex_tp
        self.new_tp = new_tp
        self.res_tp = res_tp
        self.del_tp = del_tp
        self.ch_tp = ch_tp
        self.residua_tp = residua_tp

        self.res_points = res_points
        self.del_points = del_points

        self.temp_folder = temp_folder
        self.dat_folder = dat_folder

        self.proj_file = proj_file
        self.current_file_proj = current_file_proj
        self.old_file_proj = old_file_proj

        self.temp_ex_file = temp_ex_file
        self.temp_new_file = temp_new_file
        self.temp_new_p_file = temp_new_p_file
        self.temp_change_p_file = temp_change_p_file
        self.temp_dump_file = temp_dump_file
        self.temp_steps_file = temp_steps_file
        self.temp_new_out_file = temp_new_out_file
        self.temp_chg_out_file = temp_chg_out_file
        self.temp_dat_file = temp_dat_file
        self.temp_residuals = temp_residuals
        self.temp_compare = temp_compare

    ''' Find the highest id in a table '''
    def next_id(self, table_, coursor_):
        coursor_.execute('SELECT id FROM %s' % table_)
        id_list = coursor_.fetchall()
        if len(id_list) == 0:
            new_id = 1
        else:
            new_id = str(max(id_list)[0] + 1)
        return new_id

    ''' Find proper table and database '''
    def find_database_table(self, type_, proj_name, proj_revision):
        db_dir = self.ctn_data_id + '/' + proj_name + proj_revision + '/'
        table_ = ''
        if type_ == self.ex_tp:
            db_dir = db_dir + self.exist_db_id
            table_ = self.exist_tb_id
        elif type_ == self.dp_tp:
            db_dir = db_dir + self.dump_db_id
            table_ = self.dump_tb_id
        elif type_ == self.new_tp:
            db_dir = db_dir + self.new_db_id
            table_ = self.new_tb_id
        elif type_ == self.ch_tp:
            db_dir = db_dir + self.ch_db_id
            table_ = self.ch_tb_id
        elif type_ == self.dat_tp:
            db_dir = db_dir + self.dat_db_id
            table_ = self.dat_tb_id
        elif type_ == self.res_tp:
            db_dir = db_dir + self.dat_db_id
            table_ = self.dat_res_tb_id
        elif type_ == self.del_tp:
            db_dir = db_dir + self.dat_db_id
            table_ = self.dat_del_tb_id
        elif type_ == self.proj_tp:
            db_dir = db_dir + self.proj_db_id
            table_ = self.proj_tb_id
        elif type_ == self.residua_tp:
            db_dir = db_dir + self.res_db_id
            table_ = self.res_tb_id
        return db_dir, table_

    ''' Create database for projects '''
    def projects_db_create(self):
        dbproj_dir = self.ctn_data_id + '/' + self.proj_db_id
        if os.path.exists(self.ctn_data_id):
            if os.path.exists(dbproj_dir):
                pass
            else:
                self.create_db(dir_=dbproj_dir, type_=self.proj_tp)
        else:
            os.mkdir(self.ctn_data_id)
            self.create_db(dir_=dbproj_dir, type_=self.proj_tp)

    ''' Read all project from project database '''
    def read_projects_db(self):
        dbproj_dir = self.ctn_data_id + '/' + self.proj_db_id
        conn_ = sqlite3.connect(dbproj_dir)
        c = conn_.cursor()
        c.execute("SELECT * FROM %s" % self.proj_tb_id)
        rows = c.fetchall()
        conn_.commit()
        conn_.close()
        return rows

    ''' Read all records from database '''
    def read_table_db(self, type_, proj_name, proj_revision):
        db_dir, table_ = self.find_database_table(type_=type_, proj_name=proj_name, proj_revision=proj_revision)
        conn_ = sqlite3.connect(db_dir)
        c = conn_.cursor()
        c.execute("SELECT * FROM %s" % table_)
        rows = c.fetchall()
        conn_.commit()
        conn_.close()
        return rows

    ''' Read table information from database '''
    def read_col_db(self, type_, proj_name, proj_revision):
        db_dir, table_ = self.find_database_table(type_=type_, proj_name=proj_name, proj_revision=proj_revision)
        conn_ = sqlite3.connect(db_dir)
        c = conn_.cursor()
        c.execute('PRAGMA TABLE_INFO(%s)' % table_)
        table_info = c.fetchall()
        conn_.commit()
        conn_.close()
        return table_info

    ''' Add new project to project database '''
    def add_project_rev(self, proj_name, proj_revision, import_proj=False):
        dbproj_dir = self.ctn_data_id + '/' + self.proj_db_id
        conn_ = sqlite3.connect(dbproj_dir)
        c = conn_.cursor()
        new_id = self.next_id(table_=self.proj_tb_id, coursor_=c)
        command_ = 'INSERT INTO %s (id, name, revision) VALUES (?,?,?); ' % self.proj_tb_id
        data_tuple = (new_id, proj_name, proj_revision)
        c.execute(command_, data_tuple)
        conn_.commit()
        conn_.close()
        new_folder = self.ctn_data_id + '/' + proj_name + proj_revision
        if os.path.exists(new_folder):
            pass
        else:
            os.mkdir(new_folder)
        proj_file = new_folder + '/' + proj_name + proj_revision + self.proj_file
        json_obj = {'project': [], 'files': []}
        json_obj['project'].append({
            'project_name': proj_name,
            'project_revision': proj_revision
        })
        json_obj['files'].append({
            'dump_file': '',
            'dat_file': '',
            'existing_file': '',
            'new_points_file': '',
            'changed_points_file': '',
            'residua_file': '',
        })
        # Write the object to file.
        with open(proj_file, 'w') as jsonFile:
            json.dump(json_obj, jsonFile)
        if not import_proj:
            self.new_job(proj_name=proj_name, proj_revision=proj_revision)

    ''' Import another project as zip file to the database '''
    def import_project(self, dir_zip_file):
        self.extract_zip_file(dir_zip_file=dir_zip_file)
        proj_name, proj_revision = self.get_project_name(dir_zip_file=dir_zip_file)
        self.add_project_rev(proj_name=proj_name, proj_revision=proj_revision, import_proj=True)

    def extract_zip_file(self, dir_zip_file):
        target_dir = self.ctn_data_id
        with zipfile.ZipFile(dir_zip_file, 'r') as z:
            z.extractall(target_dir)

    def get_project_name(self, dir_zip_file):
        zip_ = zipfile.ZipFile(dir_zip_file)
        project_folder = zip_.namelist()[0]
        project_file = self.ctn_data_id + '/' + project_folder + project_folder[:-1] + self.proj_file
        with open(project_file) as f:
            data_ = json.load(f)
        project_name = data_['project'][0]['project_name']
        revision_name = data_['project'][0]['project_revision']
        return project_name, revision_name

    ''' Delete project from project database '''
    def delete_project(self, id_del):
        dbproj_dir = self.ctn_data_id + '/' + self.proj_db_id
        conn_ = sqlite3.connect(dbproj_dir)
        c = conn_.cursor()
        command_ = 'SELECT name, revision FROM %s where id = ?' % self.proj_tb_id
        c.execute(command_, (id_del,))
        proj_name, proj_revision = c.fetchall()[0]
        command_ = 'DELETE from %s where id = ?' % self.proj_tb_id
        c.execute(command_, (id_del,))
        conn_.commit()
        conn_.close()
        project_folder = self.ctn_data_id + '/' + proj_name + proj_revision
        if os.path.exists(project_folder):
            shutil.rmtree(project_folder)

    'Create new files for new project'
    def new_job(self, proj_name, proj_revision):
        new_folder = self.ctn_data_id + '/' + proj_name + proj_revision
        dbex_dir = new_folder + '/' + self.exist_db_id
        dbpt_dir = new_folder + '/' + self.dump_db_id
        dbnew_dir = new_folder + '/' + self.new_db_id
        dbdat_dir = new_folder + '/' + self.dat_db_id
        dbres_dir = new_folder + '/' + self.res_db_id
        dbch_dir = new_folder + '/' + self.ch_db_id
        temp_folder = new_folder + self.temp_folder
        dat_source_f_dir = new_folder + self.dat_folder
        temp_txt_new_p_dir = temp_folder + self.temp_new_out_file
        temp_txt_ch_p_dir = temp_folder + self.temp_chg_out_file
        temp_dat_dir = temp_folder + self.temp_dat_file
        if os.path.exists(dbex_dir):
            pass
        else:
            self.create_db(dir_=dbex_dir, type_=self.ex_tp)
            self.create_db(dir_=dbpt_dir, type_=self.dp_tp)
            self.create_db(dir_=dbnew_dir, type_=self.new_tp)
            self.create_db(dir_=dbch_dir, type_=self.ch_tp)
            self.create_db(dir_=dbdat_dir, type_=self.dat_tp)
            self.create_db(dir_=dbres_dir, type_=self.residua_tp)

            os.mkdir(temp_folder)
            self.create_temp_file(file_=self.temp_compare, temp_folder=temp_folder)
            self.create_temp_file(file_=self.temp_residuals, temp_folder=temp_folder)
            self.create_temp_file(file_=self.temp_ex_file, temp_folder=temp_folder)
            self.create_temp_file(file_=self.temp_new_file, temp_folder=temp_folder)
            self.create_temp_file(file_=self.temp_steps_file, temp_folder=temp_folder)
            self.create_temp_file(file_=self.temp_dump_file, temp_folder=temp_folder)
            self.create_temp_file(file_=self.temp_new_p_file, temp_folder=temp_folder)
            self.create_temp_file(file_=self.temp_change_p_file, temp_folder=temp_folder)

            f = open(temp_txt_new_p_dir, 'w')
            f.close()
            f = open(temp_txt_ch_p_dir, 'w')
            f.close()
            f = open(temp_dat_dir, 'w')
            f.close()
            os.mkdir(dat_source_f_dir)

    ''' Create all temporary files for new project in project directory '''
    def create_temp_file(self, file_, temp_folder):
        file_out = {}
        if file_ == self.temp_compare:
            file_out = {
                'current_project': [],
                'old_project': []
            }
            file_out['current_project'].append({
                'name': [],
                'description': [],
                'northing': [],
                'easting': [],
                'elevation': [],
                'scstddevn': [],
                'scstddeve': [],
                'scstddevz': [],
            })
            file_out['old_project'].append({
                'name': [],
                'description': [],
                'northing': [],
                'easting': [],
                'elevation': [],
                'scstddevn': [],
                'scstddeve': [],
                'scstddevz': [],
            })
        if file_ == self.temp_residuals:
            file_out = {
                'residuals': [],
            }
            file_out['residuals'].append({
                'name': [],
                'description': [],
                'northing': [],
                'easting': [],
                'elevation': [],
                'scstddevn': [],
                'scstddeve': [],
                'scstddevz': [],
                'ex_northing': [],
                'ex_easting': [],
                'ex_elevation': [],
            })
        if file_ == self.temp_ex_file:
            file_out = {
                'existing': [],
            }
            file_out['existing'].append({
                'name': [],
                'easting': [],
                'northing': [],
                'elevation': [],
                'description': [],
            })
        if file_ == self.temp_new_file:
            file_out = {
                'new': [],
            }
            file_out['new'].append({
                'name': [],
                'easting': [],
                'northing': [],
                'elevation': [],
                'description': [],
            })
        if file_ == self.temp_new_p_file:
            file_out = {
                'new': [],
            }
            file_out['new'].append({
                'name': [],
                'description': [],
                'northing': [],
                'easting': [],
                'elevation': [],
                'scstddevn': [],
                'scstddeve': [],
                'scstddevz': [],
            })
        if file_ == self.temp_change_p_file:
            file_out = {
                'change': [],
            }
            file_out['change'].append({
                'name': [],
                'description': [],
                'northing': [],
                'easting': [],
                'elevation': [],
                'scstddevn': [],
                'scstddeve': [],
                'scstddevz': [],
            })
        if file_ == self.temp_steps_file:
            file_out = {
                'steps': [],
            }
            file_out['steps'].append({
                'temporary file': [],
                'database': [],
                'procedure': [],
                'points': [],
            })
        if file_ == self.temp_dump_file:
            file_out = {
                'dump': [],
            }
            file_out['dump'].append({
                'name': [],
                'description': [],
                'northing': [],
                'easting': [],
                'elevation': [],
                'latitude': [],
                'longitude': [],
                'ellipht': [],
                'gridfactor': [],
                'elevfactor': [],
                'convergence': [],
                'scstddevn': [],
                'scstddeve': [],
                'scstddevz': [],
                'varn': [],
                'vare': [],
                'varz': [],
                'covarne': [],
                'covarnz': [],
                'covarez': [],
            })
        file_dir = temp_folder + file_
        with open(file_dir, 'w') as jsonFile:
            json.dump(file_out, jsonFile)

    ''' Create new databases for new project in project directory '''
    def create_db(self, dir_, type_):
        conn_ = sqlite3.connect(dir_)
        c = conn_.cursor()
        if type_ == self.ex_tp:
            c.execute(
                "CREATE TABLE %s (id INTEGER PRIMARY KEY, name text, easting real, northing real, elevation real, description text)" % self.exist_tb_id)
        elif type_ == self.dp_tp:
            c.execute(
                "CREATE TABLE %s (id INTEGER PRIMARY KEY, name text, description text, northing real, easting real, elevation real, latitude real, longitude real, ellipht real, gridfactor real, elevfactor real, convergence real, scstddevn real, scstddeve real, scstddevz real, varn real, vare real, varz real, covarne real, covarnz real, covarez real)" % self.dump_tb_id)
        elif type_ == self.proj_tp:
            c.execute(
                "CREATE TABLE %s (id INTEGER PRIMARY KEY, name text, revision text)" % self.proj_tb_id)
        elif type_ == self.new_tp:
            c.execute(
                "CREATE TABLE %s (id INTEGER PRIMARY KEY, name text, description text, easting real, northing real, elevation real, scstddevn real, scstddeve real, scstddevz real)" % self.new_tb_id)
        elif type_ == self.ch_tp:
            c.execute(
                "CREATE TABLE %s (id INTEGER PRIMARY KEY, name text, description text, easting real, northing real, elevation real, scstddevn real, scstddeve real, scstddevz real)" % self.ch_tb_id)
        elif type_ == self.dat_tp:
            c.execute(
                "CREATE TABLE %s (id INTEGER PRIMARY KEY, file_dir text)" % self.dat_tb_id)
            c.execute(
                "CREATE TABLE %s (id INTEGER PRIMARY KEY, resection_name text)" % self.dat_res_tb_id)
            c.execute(
                "CREATE TABLE %s (id INTEGER PRIMARY KEY, delete_name text)" % self.dat_del_tb_id)
        elif type_ == self.residua_tp:
            c.execute(
                "CREATE TABLE %s (id INTEGER PRIMARY KEY, name text, description text, northing real, easting real, elevation real, scstddevn real, scstddeve real, scstddevz real, ex_northing, ex_easting, ex_elevation)" % self.res_tb_id)
        conn_.commit()
        conn_.close()

    ''' Import file (existing points, dump file or dat file) to the database '''
    def import_file(self, file_dir, type_, proj_name, proj_revision):
        """ File check """
        # pozniej sie tym zajme #

        """ File import """
        db_dir = self.ctn_data_id + '/' + proj_name + proj_revision + '/'
        if type_ == self.ex_tp or type_ == self.dp_tp:
            table_ = ''
            if type_ == self.ex_tp:
                db_dir = db_dir + self.exist_db_id
                table_ = self.exist_tb_id
            elif type_ == self.dp_tp:
                db_dir = db_dir + self.dump_db_id
                table_ = self.dump_tb_id
            conn_ = sqlite3.connect(db_dir)
            pd.read_csv(file_dir).to_sql(table_, conn_, if_exists='append', index=False)
            conn_.commit()
            conn_.close()
        elif type_ == self.dat_tp:
            dat_source_f_dir = db_dir + self.dat_folder
            shutil.copy(file_dir, dat_source_f_dir)
            db_dir = db_dir + self.dat_db_id
            conn_ = sqlite3.connect(db_dir)
            c = conn_.cursor()
            new_id = self.next_id(table_=self.dat_tb_id, coursor_=c)
            command_ = 'INSERT INTO %s (id, file_dir) VALUES (?,?); ' % self.dat_tb_id
            for dat_file in os.listdir(dat_source_f_dir):
                data_tuple = (new_id, dat_file)
                c.execute(command_, data_tuple)
                new_id = str(int(new_id) + 1)
            conn_.commit()
            conn_.close()

    ''' Read dat file to remove all resections and non important points'''
    def read_dat_file(self, proj_name, proj_revision, id_file):
        db_dir = self.ctn_data_id + '/' + proj_name + proj_revision + '/'
        dat_dir = self.ctn_data_id + '/' + proj_name + proj_revision + self.dat_folder + '/'
        db_dir = db_dir + self.dat_db_id
        conn_ = sqlite3.connect(db_dir)
        c = conn_.cursor()
        command_ = 'SELECT file_dir FROM %s where id = ?' % self.dat_tb_id
        c.execute(command_, (id_file,))
        file_dir = c.fetchall()[0]
        f_ = open((dat_dir + file_dir[0]), 'r')
        f_lines = f_.readlines()
        command_res = 'INSERT INTO %s (id, resection_name) VALUES (?,?); ' % self.dat_res_tb_id
        command_del = 'INSERT INTO %s (id, delete_name) VALUES (?,?); ' % self.dat_del_tb_id
        for i in range(len(f_lines)):
            if f_lines[i][0:4] == self.res_points:
                new_id = self.next_id(table_=self.dat_res_tb_id, coursor_=c)
                line_list = f_lines[i+1].split()
                resection_ = line_list[1]
                data_tuple = (new_id, resection_)
                c.execute(command_res, data_tuple)
                c.execute("SELECT * FROM %s" % self.dat_res_tb_id)
            if f_lines[i][0:4] == self.del_points:
                new_id = self.next_id(table_=self.dat_del_tb_id, coursor_=c)
                line_list = f_lines[i+1].split()
                delete_ = line_list[1]
                data_tuple = (str(new_id), delete_)
                c.execute(command_del, data_tuple)
        conn_.commit()
        conn_.close()

    ''' Save new information to project json file '''
    def save_to_project(self, proj_name, proj_revision, type_):
        proj_folder = self.ctn_data_id + '/' + proj_name + proj_revision
        if os.path.exists(proj_folder):
            proj_file = proj_folder + '/' + proj_name + proj_revision + self.proj_file
            current_file = './temp/current_proj.json'
            if os.path.exists(proj_file):
                with open(proj_file) as f:
                    data_ = json.load(f)
                with open(current_file) as f_c:
                    data_c = json.load(f_c)
                if proj_name == data_['project'][0]['project_name']:
                    if proj_revision == data_['project'][0]['project_revision']:
                        if type_ == self.dp_tp:
                            dump_save = proj_folder + '/' + self.dump_db_id
                            data_['files'][0]['dump_file'] = dump_save
                            data_c['files'][0]['dump_file'] = dump_save
                        elif type_ == self.dat_tp:
                            dat_save = proj_folder + '/' + self.dat_db_id
                            data_['files'][0]['dat_file'] = dat_save
                            data_c['files'][0]['dat_file'] = dat_save
                        elif type_ == self.ex_tp:
                            ex_save = proj_folder + '/' + self.exist_db_id
                            data_['files'][0]['existing_file'] = ex_save
                            data_c['files'][0]['existing_file'] = ex_save
                        elif type_ == self.new_tp:
                            new_save = proj_folder + '/' + self.new_db_id
                            data_['files'][0]['new_points_file'] = new_save
                            data_c['files'][0]['new_points_file'] = new_save
                        elif type_ == self.ch_tp:
                            ch_save = proj_folder + '/' + self.ch_db_id
                            data_['files'][0]['changed_points_file'] = ch_save
                            data_c['files'][0]['changed_points_file'] = ch_save
                        elif type_ == self.residua_tp:
                            res_save = proj_folder + '/' + self.res_db_id
                            data_['files'][0]['residua_file'] = res_save
                            data_c['files'][0]['residua_file'] = res_save
                        with open(proj_file, 'w') as jsonFile:
                            json.dump(data_, jsonFile)
                        with open(current_file, 'w') as jsonFile2:
                            json.dump(data_c, jsonFile2)

    ''' Delete all data from the table '''
    def delete_all(self, type_, proj_name, proj_revision):
        db_dir, table_ = self.find_database_table(type_=type_, proj_name=proj_name, proj_revision=proj_revision)
        conn_ = sqlite3.connect(db_dir)
        c = conn_.cursor()
        c.execute("DELETE FROM %s" % table_)
        conn_.commit()
        conn_.close()

    ''' Delete one record or list of records from the table '''
    def delete_one_row(self, id_del, type_, proj_name, proj_revision, if_list=False):
        db_dir, table_ = self.find_database_table(type_=type_, proj_name=proj_name, proj_revision=proj_revision)
        conn_ = sqlite3.connect(db_dir)
        c = conn_.cursor()
        if not if_list:
            command_ = 'DELETE from %s where id = ?' % table_
            c.execute(command_, (id_del,))
        else:
            first_command_ = 'DELETE FROM %s WHERE id = ' % table_
            for item in id_del:
                command_ = first_command_ + '%s' % item
                c.execute(command_)
        conn_.commit()
        conn_.close()

    ''' Read temporary files '''
    def read_temp_file(self, file, proj_name, proj_revision):
        if len(proj_name) > 0 and len(proj_revision) > 0:
            proj_folder = self.ctn_data_id + '/' + proj_name + proj_revision + self.temp_folder
            file_dir = proj_folder + file
            with open(file_dir) as f:
                data_ = json.load(f)
            data_con = []
            current_, old_, residua_, new_ex, new_dump = [], [], [], [], []
            if file == self.temp_compare:
                current_.append(data_['current_project'][0]['name'])
                current_.append(data_['current_project'][0]['description'])
                current_.append(data_['current_project'][0]['northing'])
                current_.append(data_['current_project'][0]['easting'])
                current_.append(data_['current_project'][0]['elevation'])
                current_.append(data_['current_project'][0]['scstddevn'])
                current_.append(data_['current_project'][0]['scstddeve'])
                current_.append(data_['current_project'][0]['scstddevz'])
                old_.append(data_['old_project'][0]['name'])
                old_.append(data_['old_project'][0]['description'])
                old_.append(data_['old_project'][0]['northing'])
                old_.append(data_['old_project'][0]['easting'])
                old_.append(data_['old_project'][0]['elevation'])
                old_.append(data_['old_project'][0]['scstddevn'])
                old_.append(data_['old_project'][0]['scstddeve'])
                old_.append(data_['old_project'][0]['scstddevz'])
                data_con = [current_, old_]
            if file == self.temp_residuals:
                residua_.append(data_['residuals'][0]['name'])
                residua_.append(data_['residuals'][0]['description'])
                residua_.append(data_['residuals'][0]['northing'])
                residua_.append(data_['residuals'][0]['easting'])
                residua_.append(data_['residuals'][0]['elevation'])
                residua_.append(data_['residuals'][0]['scstddevn'])
                residua_.append(data_['residuals'][0]['scstddeve'])
                residua_.append(data_['residuals'][0]['scstddevz'])
                residua_.append(data_['residuals'][0]['ex_northing'])
                residua_.append(data_['residuals'][0]['ex_easting'])
                residua_.append(data_['residuals'][0]['ex_elevation'])
                data_con = residua_
            if file == self.temp_ex_file:
                new_ex.append(data_['existing'][0]['name'])
                new_ex.append(data_['existing'][0]['easting'])
                new_ex.append(data_['existing'][0]['northing'])
                new_ex.append(data_['existing'][0]['elevation'])
                new_ex.append(data_['existing'][0]['description'])
                data_con = new_ex
            if file == self.temp_new_p_file:
                new_dump.append(data_['new'][0]['name'])
                new_dump.append(data_['new'][0]['description'])
                new_dump.append(data_['new'][0]['northing'])
                new_dump.append(data_['new'][0]['easting'])
                new_dump.append(data_['new'][0]['elevation'])
                new_dump.append(data_['new'][0]['scstddevn'])
                new_dump.append(data_['new'][0]['scstddeve'])
                new_dump.append(data_['new'][0]['scstddevz'])
                data_con = new_dump
            return data_con

    ''' 
    Dump data in temporary .json format files.
    For comparison temporary file data must be in order: 
        - [Current project [data], Old project [data]]
            - [data[name[], description[], northing[], easting[], elevation[], scstddevn[], scstddeve[], scstddevz[]]]
    '''
    def dump_temp_file(self, file, proj_name, proj_revision, data_out):
        if len(proj_name) > 0 and len(proj_revision) > 0:
            proj_folder = self.ctn_data_id + '/' + proj_name + proj_revision + self.temp_folder
            file_dir = proj_folder + file
            with open(file_dir) as f:
                data_ = json.load(f)
            if file == self.temp_compare:
                n_proj = data_out[0]
                o_proj = data_out[1]
                data_['current_project'][0]['name'] = n_proj[0, :].tolist()
                data_['current_project'][0]['description'] = n_proj[1, :].tolist()
                data_['current_project'][0]['northing'] = n_proj[2, :].tolist()
                data_['current_project'][0]['easting'] = n_proj[3, :].tolist()
                data_['current_project'][0]['elevation'] = n_proj[4, :].tolist()
                data_['current_project'][0]['scstddevn'] = n_proj[5, :].tolist()
                data_['current_project'][0]['scstddeve'] = n_proj[6, :].tolist()
                data_['current_project'][0]['scstddevz'] = n_proj[7, :].tolist()
                data_['old_project'][0]['name'] = o_proj[0, :].tolist()
                data_['old_project'][0]['description'] = o_proj[1, :].tolist()
                data_['old_project'][0]['northing'] = o_proj[2, :].tolist()
                data_['old_project'][0]['easting'] = o_proj[3, :].tolist()
                data_['old_project'][0]['elevation'] = o_proj[4, :].tolist()
                data_['old_project'][0]['scstddevn'] = o_proj[5, :].tolist()
                data_['old_project'][0]['scstddeve'] = o_proj[6, :].tolist()
                data_['old_project'][0]['scstddevz'] = o_proj[7, :].tolist()
            elif file == self.temp_residuals:
                residuals_ = data_out
                data_['residuals'][0]['name'] = residuals_[0, :].tolist()
                data_['residuals'][0]['description'] = residuals_[1, :].tolist()
                data_['residuals'][0]['northing'] = residuals_[2, :].tolist()
                data_['residuals'][0]['easting'] = residuals_[3, :].tolist()
                data_['residuals'][0]['elevation'] = residuals_[4, :].tolist()
                data_['residuals'][0]['scstddevn'] = residuals_[5, :].tolist()
                data_['residuals'][0]['scstddeve'] = residuals_[6, :].tolist()
                data_['residuals'][0]['scstddevz'] = residuals_[7, :].tolist()
                data_['residuals'][0]['ex_northing'] = residuals_[8, :].tolist()
                data_['residuals'][0]['ex_easting'] = residuals_[9, :].tolist()
                data_['residuals'][0]['ex_elevation'] = residuals_[10, :].tolist()
            elif file == self.temp_ex_file:
                existing_ = data_out
                data_['existing'][0]['name'] = existing_[0, :].tolist()
                data_['existing'][0]['easting'] = existing_[1, :].tolist()
                data_['existing'][0]['northing'] = existing_[2, :].tolist()
                data_['existing'][0]['elevation'] = existing_[3, :].tolist()
                data_['existing'][0]['description'] = existing_[4, :].tolist()
            elif file == self.temp_steps_file:
                steps = data_out
                data_['steps'][0]['temporary file'].append(steps[0])
                data_['steps'][0]['database'].append(steps[1])
                data_['steps'][0]['procedure'].append(steps[2])
                data_['steps'][0]['points'].append(steps[3])
            elif file == self.temp_new_p_file:
                new_ = data_out
                data_['new'][0]['name'] = new_[0, :].tolist()
                data_['new'][0]['description'] = new_[1, :].tolist()
                data_['new'][0]['northing'] = new_[2, :].tolist()
                data_['new'][0]['easting'] = new_[3, :].tolist()
                data_['new'][0]['elevation'] = new_[4, :].tolist()
                data_['new'][0]['scstddevn'] = new_[5, :].tolist()
                data_['new'][0]['scstddeve'] = new_[6, :].tolist()
                data_['new'][0]['scstddevz'] = new_[7, :].tolist()
            elif file == self.temp_change_p_file:
                change_ = data_out
                data_['change'][0]['name'] = change_[0, :].tolist()
                data_['change'][0]['description'] = change_[1, :].tolist()
                data_['change'][0]['northing'] = change_[2, :].tolist()
                data_['change'][0]['easting'] = change_[3, :].tolist()
                data_['change'][0]['elevation'] = change_[4, :].tolist()
                data_['change'][0]['scstddevn'] = change_[5, :].tolist()
                data_['change'][0]['scstddeve'] = change_[6, :].tolist()
                data_['change'][0]['scstddevz'] = change_[7, :].tolist()

            with open(file_dir, 'w') as jsonFile:
                json.dump(data_, jsonFile)

    ''' 
    Back procedure:
    - open the steps file and find the last recorded step
    - read the information about database and points involved
    - find the record of the points in this database
    - remove the last recorded step from steps file
    - return the record about points
    '''
    def back_result(self, proj_name, proj_revision, last_remove=True):
        proj_folder = self.ctn_data_id + '/' + proj_name + proj_revision
        temp_folder = proj_folder + self.temp_folder
        file_steps = temp_folder + self.temp_steps_file
        with open(file_steps) as f:
            data_steps = json.load(f)
        before_array = []
        if len(data_steps['steps'][0]['database']) > 0:
            db_type = data_steps['steps'][0]['database'][-1][0]
            points_ = data_steps['steps'][0]['points'][-1]
            procedure_ = data_steps['steps'][0]['procedure'][-1]
            db_dir, table_ = self.find_database_table(type_=db_type, proj_name=proj_name, proj_revision=proj_revision)
            conn_ = sqlite3.connect(db_dir)
            c = conn_.cursor()

            command_ = 'SELECT * FROM %s where name = ?' % table_
            if np.size(points_) > 1:
                for i in range(len(points_)):
                    c.execute(command_, (points_[i],))
                    row_ = c.fetchall()[0]
                    before_array.append(row_)
            else:
                c.execute(command_, (points_,))
                row_ = c.fetchall()[0]
                before_array.append(row_)
            conn_.commit()
            conn_.close()
            if last_remove:
                data_steps['steps'][0]['temporary file'] = data_steps['steps'][0]['temporary file'][0:-1]
                data_steps['steps'][0]['database'] = data_steps['steps'][0]['database'][0:-1]
                data_steps['steps'][0]['procedure'] = data_steps['steps'][0]['procedure'][0:-1]
                data_steps['steps'][0]['points'] = data_steps['steps'][0]['points'][0:-1]
                with open(file_steps, 'w') as jsonFile:
                    json.dump(data_steps, jsonFile)

        return before_array, procedure_[0]

    ''' 
    Dump data into particular database.
    '''
    def dump_database(self, type_, proj_name, proj_revision, data_out):
        db_dir, table_ = self.find_database_table(type_=type_, proj_name=proj_name, proj_revision=proj_revision)
        self.delete_all(type_=type_, proj_name=proj_name, proj_revision=proj_revision)
        table_info = self.read_col_db(type_=type_, proj_name=proj_name, proj_revision=proj_revision)
        conn_ = sqlite3.connect(db_dir)
        c = conn_.cursor()
        col_names_all = [col_[1] for col_ in table_info]
        values_ = '('
        for i in range(len(col_names_all) - 1):
            values_ = values_ + '?,'
        values_ = values_ + '?); '
        command_ = 'INSERT INTO %s VALUES ' + values_
        command_ = command_ % table_
        if len(data_out[0, :]) > 1:
            for i in range(len(data_out[0, :])):
                new_id = self.next_id(table_=table_, coursor_=c)
                row_out = data_out[:, i].tolist()
                row_out = [str(new_id)] + row_out
                data_tuple = tuple(row_out)
                c.execute(command_, data_tuple)
        else:
            new_id = self.next_id(table_=table_, coursor_=c)
            row_out = data_out.tolist()
            row_out = [str(new_id)] + row_out
            data_tuple = tuple(row_out)
            c.execute(command_, data_tuple)
        conn_.commit()
        conn_.close()

