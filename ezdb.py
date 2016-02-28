#!/usr/bin/env python

import npyscreen
import postgres_db as pdb
import mysql_db as mdb
import time


# ActionForm includes "Cancel" in addition to "OK"
class Initial(npyscreen.ActionForm, npyscreen.SplitForm):
    sessionType, db = None, None

    def create(self):
        # Title text
        self.nextrely += 5  # Move down
        self.nextrelx += 45  # Move right (centered))
        self.add(npyscreen.FixedText, value="                _  _     ", editable=False)
        self.add(npyscreen.FixedText, value="               | || |    ", editable=False)
        self.add(npyscreen.FixedText, value="  ___  ____  __| || |__  ", editable=False)
        self.add(npyscreen.FixedText, value=" / _ \|_  / / _` || '_ \ ", editable=False)
        self.add(npyscreen.FixedText, value="|  __/ / / | (_| || |_) |", editable=False)
        self.add(npyscreen.FixedText, value=" \___|/___| \__,_||_.__/ ", editable=False)

        # Add session options and save the selected value
        self.nextrely += 4  # Move down
        self.nextrelx += 2  # Move right (centered)
        self.add(npyscreen.FixedText, value="Choose Database Type:", editable=False)
        self.db = self.add(npyscreen.SelectOne, max_height=2, value=[0], values=["postgreSQL", "MySQL"],
                           scroll_exit=True)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Select the database type with which you'd like to interact this session. This application " \
                   "supports MySQL and PostgreSQL database systems."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def on_ok(self):
        # For debugging:
        # npyscreen.notify_confirm("You selected " + str(self.db.value[0]))
        self.parentApp.dbtype = self.db.value[0]
        self.parentApp.setNextForm("ConnectDBMS")

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=2)
        if exiting:
            self.parentApp.setNextForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class ConnectDBMS(npyscreen.ActionForm, npyscreen.SplitForm):
    storedConnections, result, dbtype = (None,)*3

    def create(self):
        # Set default DBMS connection values
        # For debugging:
        # npyscreen.notify_confirm("The value of dbtype in ConnectDBMS is " + str(dbtype))
        if self.parentApp.dbtype == 0:
            self.add(npyscreen.FixedText, value="Enter PostgreSQL Database System Connection Settings:", editable=False)
            self.parentApp.port = '5432'
            self.parentApp.username = 'postgres'
            self.parentApp.password = 'password'
        elif self.parentApp.dbtype == 1:
            self.add(npyscreen.FixedText, value="Enter MySQL Database System Connection Settings:", editable=False)
            self.parentApp.port = '3306'
            self.parentApp.username = 'root'
            self.parentApp.password = 'password'

        self.nextrely += 2  # Move down
        self.parentApp.host = self.add(npyscreen.TitleText, name="Hostname:", value="127.0.0.1")
        self.nextrely += 1  # Move down
        self.parentApp.port = self.add(npyscreen.TitleText, name="Port:", value=self.parentApp.port)
        self.nextrely += 1  # Move down
        self.parentApp.username = self.add(npyscreen.TitleText, name="Username:", value=self.parentApp.username)
        self.nextrely += 1  # Move down
        self.parentApp.password = self.add(npyscreen.TitleText, name="Password:", value=self.parentApp.password)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Enter the connection settings for the database system with which you'd like to interact. The " \
                   "initial settings are the default settings for local databases."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def on_ok(self):
        self.result = None

        # Connect to DBMS
        if self.parentApp.dbtype == 0:
            self.parentApp.dbms = pdb.Postgres_Database()
            self.result = self.parentApp.dbms.connect_DBMS(self.parentApp.dbtype, self.parentApp.host.value,
                                                           self.parentApp.port.value, self.parentApp.username.value,
                                                           self.parentApp.password.value)

        elif self.parentApp.dbtype == 1:
            self.parentApp.dbms = mdb.MySQL_Database()
            self.result = self.parentApp.dbms.connect_DBMS(self.parentApp.dbtype, self.parentApp.host.value,
                                                           self.parentApp.port.value, self.parentApp.username.value,
                                                           self.parentApp.password.value)

        if self.result is not None:
            npyscreen.notify_confirm("There was a problem connecting to the database system:\n" + str(self.result))
            self.result = None
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
        else:
            self.parentApp.setNextForm("DatabaseWindow")

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class DatabaseWindow(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit, dbList, dbtype_str = (None,)*9

    def create(self):

        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True, color="VERYGOOD")
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        self.dbList = self.parentApp.dbms.list_databases()

        self.nextrely += 1  # Move down

        if self.parentApp.dbtype == 0:
            self.dbtype_str = "PostgreSQL"
        elif self.parentApp.dbtype == 1:
            self.dbtype_str = "MySQL"

        self.add(npyscreen.BoxTitle, w_id="wDatabases_box", name="{} Databases".format(self.dbtype_str),
                 values=self.parentApp.dbms.list_databases(), max_width=30, max_height=17, scroll_exit=True)

        # Database button options
        self.nextrely += 1  # Move down
        self.add(OpenDBButton, name="Open Database")

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wNewDB_name", name="New Database Name:", relx=4,
                 begin_entry_at=22, use_two_lines=False)

        self.add(CreateDBButton, name="Create")

        self.nextrely += 1  # Move down
        self.add(DeleteDBButton, name="Delete Database")

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Select an available database instance from the list, and choose \"Open Database\" to begin " \
                   "interaction. If no instances are available, create a new one or contact your database administer."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class TablesWindow(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = (None,)*7

    def create(self):
        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31, color="VERYGOOD")
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45)

        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        self.nextrely += 1  # Move down
        self.add(npyscreen.FixedText, value="Database: {}".format(self.parentApp.active_db), relx=3, color="LABEL",
                 editable=False)

        self.nextrely += 1  # Move down
        self.add(npyscreen.BoxTitle, w_id="wTables_box", name="Tables",
                 values=self.parentApp.tableList, max_width=25, max_height=11, scroll_exit=True)

        self.nextrely += 1  # Move down
        self.add(BrowseTableButton, name="Browse Table", rely=6, relx=30, max_width=12)

        self.nextrely += 1  # Move down
        self.add(ViewTableStructButton, name="View Table Structure", relx=30, max_width=22)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wNewTable_name", name="New Table Name:",
                 relx=32, max_width=35, use_two_lines=False)

        self.add(BuildTableButton, name="Build", relx=30, max_width=35)

        self.nextrely += 1  # Move down
        self.add(DeleteTableButton, name="Delete Table", relx=30, max_width=35)

        self.nextrely += 3  # Move down

        self.gridbox_results = self.add(Grid_Box_Results, max_height=14, values=self.parentApp.table_results,
                                        default_column_number=10, w_id="wGrid_Box_Results",
                                        contained_widget_arguments = {"col_titles": self.parentApp.col_titles},
                                        col_margin=1, column_width=20, name="Table Results")

        self.nextrely += 1  # Move down
        self.numrecords = self.add(npyscreen.FixedText, value="{} Records Found".format(self.parentApp.num_records),
                                   editable=False)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Select an available table from the list and choose \"View Table Structure\" to view the table's " \
                   "fields and their associated constraints. Similarly, you can select a table and choose " \
                   "\"Browse Table\" to view rows (data) within the table. To define and add a new table to the " \
                   "current database instance, specify a name for the new table and choose \"Build\". Choosing " \
                   "\"Delete Table\" will permanently remove the currently selected table and all of its contents " \
                   "from the database instance."
        npyscreen.notify_confirm(help_msg, title='Help Menu')

    # PEP8 Ignore (external library naming convention)
    def beforeEditing(self):
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.get_widget("wTables_box").display()

        #clear grid widget results and num records on page load
        self.parentApp.col_titles = []
        self.gridbox_results.entry_widget.col_titles = self.parentApp.col_titles
        self.parentApp.table_results = []
        self.gridbox_results.values = self.parentApp.table_results
        self.gridbox_results.display()

        self.parentApp.num_records = 0
        self.numrecords.value = "{} Records Found".format(self.parentApp.num_records)
        self.numrecords.display()

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class TableCreatePostgreSQLForm(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):
        postgresql_field_type_list = ['CHAR', 'VARCHAR', 'TEXT', 'BIT', 'VARBIT', 'SMALLINT', 'INT', 'BIGINT',
                                      'SMALLSERIAL', 'SERIAL', 'BIGSERIAL', 'NUMERIC', 'DOUBLE PRECISION', 'REAL',
                                      'MONEY', 'BOOL', 'DATE', 'TIMESTAMP', 'TIMESTAMP WITH TIME ZONE', 'TIME',
                                      'TIME WITH TIME ZONE', 'BYTEA']

        postgresql_field_collat_list = [None, 'en_US.utf8', 'C', 'POSIX', 'C.UTF-8', 'en_AG', 'en_AG.utf8',
                                        'en_AU.utf8', 'en_AU.utf8', 'en_BW.utf8', 'en_BW.utf8', 'en_CA.utf8',
                                        'en_CA.utf8', 'en_DK.utf8', 'en_DK.utf8', 'en_GB.utf8', 'en_GB.utf8',
                                        'en_HK.utf8', 'en_HK.utf8', 'en_IE.utf8', 'en_IE.utf8', 'en_IN', 'en_IN.utf8',
                                        'en_NG', 'en_NG.utf8', 'en_NZ.utf8', 'en_NZ.utf8', 'en_PH.utf8', 'en_SG.utf8',
                                        'en_SG.utf8', 'en_ZA.utf8', 'en_ZA.utf8', 'en_ZM', 'en_ZM.utf8', 'en_ZW.utf8',
                                        'en_ZW.utf8']

        postgresql_field_constraint_list = [None, 'PRIMARY KEY', 'UNIQUE']

        self.add(npyscreen.TitleText, w_id="wField_name", name="Field Name: ", max_width=35, begin_entry_at=15,
                 use_two_lines=False)
        self.add(npyscreen.TitleSelectOne, w_id="wField_type", max_height=4, name="Type: ", value=[0],
                 values=postgresql_field_type_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wField_length_or_val", name="Length/Value: ", max_width=35,
                 begin_entry_at=15, use_two_lines=False)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wCollation", max_height=4, name="Collation: ", value=[0],
                 values=postgresql_field_collat_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wConstraint", max_height=4, name="Constraint: ", value=[0],
                 values=postgresql_field_constraint_list, rely=2, relx=40, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.SelectOne, w_id="wNot_null", values=["Not Required", "Required"], value=[0],
                 max_width=20, max_height=4, relx=40)

        # self.add(npyscreen.Checkbox, w_id="wAuto_increment", name="Auto Increment?", relx=40)
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wDefault", name="Default: ", max_width=35, relx=40)

        self.nextrely += 2  # Move down
        self.add(AddFieldButton, name="Add Field", relx=40, max_width=13)
        self.add(CreateTableButton, name="Create Table", relx=40, max_width=13)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Enter in a name for a field (column) you would like to add to the new table. Choose a field " \
                   "type for the type of information you would like the field to contain, for example \"VARCHAR\" " \
                    "for text strings or  \"INT\" for integers. Add constraints as desired, for example " \
                   "\"REQUIRED\" means a row cannot be added with a blank entry for field, and \"PRIMARY KEY\" marks" \
                   "the data in this field as the primary key for references to this table. Finally, you can add " \
                   "additional fields as needed before creating the table, or if you're ready to create, choose " \
                   "\"CREATE TABLE\"."

        npyscreen.notify_confirm(help_msg, title='Help Menu')

    def on_ok(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")

    def on_cancel(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")


class TableCreateMySQLForm(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):
        mysql_field_type_list = ['CHAR','VARCHAR','TINYTEXT','TEXT','MEDIUMTEXT','LONGTEXT',
                                 'TINYINT','SMALLINT','MEDIUMINT','INT','BIGINT','FLOAT','DOUBLE',
                                 'DECIMAL','NUMERIC', 'REAL','DATE','DATETIME','TIMESTAMP','TIME','YEAR',
                                 'TINYBLOB','BLOB','MEDIUMBLOB','LONGBLOB',
                                 'ENUM','SET','BIT','BOOL','BINARY','VARBINARY']

        mysql_field_collat_list = [None,
            'armscii8_bin','armscii8_general_ci','ascii_bin','ascii_general_ci','big5_bin','big5_chinese_ci','binary',
            'cp1250_bin','cp1250_croatian_ci','cp1250_czech_cs','cp1250_general_ci','cp1250_polish_ci','cp1251_bin',
            'cp1251_bulgarian_ci','cp1251_general_ci','cp1251_general_cs','cp1251_ukranian_ci','cp1256_bin',
            'cp1256_general_ci','cp1257_bin','cp1257_general_ci','cp1257_lithuanian_ci','cp850_bin','cp850_general_ci',
            'cp852_bin','cp852_general_ci','cp866_bin','cp866_general_ci','cp932_bin','cp932_japanese_ci','dec8_bin',
            'dec8_swedish_ci','eucjpms_bin','eucjpms_japanese_ci','euckr_bin','euckr_korean_ci','gb2312_bin',
            'gb2312_chinese_ci','gbk_bin','gbk_chinese_ci','geostd8_bin','geostd8_general_ci','greek_bin','greek_general_ci',
            'hebrew_bin','hebrew_general_ci','hp8_bin','hp8_english_ci','keybcs2_bin','keybcs2_general_ci','koi8r_bin',
            'koi8r_general_ci','latin1_bin','latin1_danish_ci','latin1_general_ci','latin1_general_cs','latin1_german1_ci',
            'latin1_german2_ci','latin1_spanish_ci','latin1_swedish_ci','latin2_bin','latin2_croatian_ci','latin2_czech_cs',
            'latin2_general_ci','latin2_hungarian_ci','latin5_bin','latin5_turkish_ci','latin7_bin','latin7_estonian_cs',
            'latin7_general_ci','latin7_general_cs','macce_bin','macce_general_ci','macroman_bin','macroman_general_ci',
            'sjis_bin','sjis_japanese_ci','swe7_bin','swe7_swedish_ci','tis620_bin','tis620_thai_ci','ucs2_bin',
            'ucs2_czech_ci','ucs2_danish_ci','ucs2_esperanto_ci','ucs2_estonian_ci','ucs2_general_ci',
            'ucs2_general_mysql500_ci','ucs2_hungarian_ci','ucs2_icelandic_ci','ucs2_latvian_ci','ucs2_lithuanian_ci',
            'ucs2_persian_ci','ucs2_polish_ci','ucs2_roman_ci','ucs2_romanian_ci','ucs2_sinhala_ci','ucs2_slovak_ci',
            'ucs2_slovenian_ci','ucs2_spanish_ci','ucs2_spanish2_ci','ucs2_swedish_ci','ucs2_turkish_ci','ucs2_unicode_ci',
            'ujis_bin','ujis_japanese_ci','utf8_bin','utf8_czech_ci','utf8_danish_ci', 'utf8_esperanto_ci',
            'utf8_estonian_ci','utf8_general_ci','utf8_general_mysql500_ci','utf8_hungarian_ci','utf8_icelandic_ci',
            'utf8_latvian_ci','utf8_lithuanian_ci','utf8_persian_ci','utf8_polish_ci','utf8_roman_ci','utf8_romanian_ci',
            'utf8_sinhala_ci','utf8_slovak_ci','utf8_slovenian_ci','utf8_spanish_ci','utf8_spanish2_ci','utf8_swedish_ci',
            'utf8_turkish_ci','utf8_unicode_ci','utf8mb4_bin','utf8mb4_czech_ci','utf8mb4_danish_ci', 'utf8mb4_esperanto_ci',
            'utf8mb4_estonian_ci','utf8mb4_general_ci','utf8mb4_hungarian_ci','utf8mb4_icelandic_ci','utf8mb4_latvian_ci',
            'utf8mb4_lithuanian_ci','utf8mb4_persian_ci','utf8mb4_polish_ci','utf8mb4_roman_ci','utf8mb4_romanian_ci',
            'utf8mb4_sinhala_ci','utf8mb4_slovak_ci','utf8mb4_slovenian_ci','utf8mb4_spanish_ci','utf8mb4_spanish2_ci',
            'utf8mb4_swedish_ci','utf8mb4_turkish_ci','utf8mb4_unicode_ci','utf16_bin','utf16_czech_ci','utf16_danish_ci',
            'utf16_esperanto_ci','utf16_estonian_ci','utf16_general_ci','utf16_hungarian_ci','utf16_icelandic_ci',
            'utf16_latvian_ci','utf16_lithuanian_ci','utf16_persian_ci','utf16_polish_ci','utf16_roman_ci','utf16_romanian_ci',
            'utf16_sinhala_ci','utf16_slovak_ci','utf16_slovenian_ci','utf16_spanish_ci','utf16_spanish2_ci',
            'utf16_swedish_ci','utf16_turkish_ci','utf16_unicode_ci','utf32_bin','utf32_czech_ci','utf32_danish_ci',
            'utf32_esperanto_ci','utf32_estonian_ci','utf32_general_ci','utf32_hungarian_ci','utf32_icelandic_ci',
            'utf32_latvian_ci','utf32_lithuanian_ci','utf32_persian_ci','utf32_polish_ci','utf32_roman_ci',
            'utf32_romanian_ci','utf32_sinhala_ci','utf32_slovak_ci','utf32_slovenian_ci','utf32_spanish_ci',
            'utf32_spanish2_ci','utf32_swedish_ci','utf32_turkish_ci','utf32_unicode_ci']

        mysql_field_attrib_list = [None, 'binary','unsigned','unsigned zerofill','on update current_timestamp']
        mysql_field_constraint_list = [None, 'PRIMARY KEY','UNIQUE','INDEX']
        mysql_engine_list = ['InnoDB','MyISAM','MRG_MYISAM','CSV','MEMORY','BLACKHOLE','PERFORMANCE_SCHEMA','ARCHIVE']

        self.add(npyscreen.TitleText, w_id="wField_name", name="Field Name: ", max_width=35, relx=2,
                 use_two_lines=False)

        self.add(npyscreen.TitleSelectOne, w_id="wField_type", max_height=5, name="Type: ", value=[0],
                 values=mysql_field_type_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wField_length_or_val", name="Length/Value: ", max_width=35,
                 use_two_lines=False)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wCollation", max_height=4, name="Collation: ", value=[0],
                 values=mysql_field_collat_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wAttribute", max_height=5, name="Attribute: ", value=[0],
                 values=mysql_field_attrib_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wConstraint", max_height=4, name="Constraint: ", value=[0],
                 values=mysql_field_constraint_list, rely=2, relx=40, max_width=37)

        self.nextrely += 1  # Move down
        self.add(npyscreen.SelectOne, w_id="wNot_null", values=["Not Required", "Required"], value=[0],
                 max_width=20, max_height=2, relx=40)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wDefault", name="Default: ", max_width=25, relx=40)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wAuto_increment", name="Auto Increment: ", values=["No", "Yes"], value=[0],
                 max_width=37, max_height=2, relx=40, use_two_lines=False)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wStorage_engine", max_height=4, name="Engine: ", value=[0],
                 values=mysql_engine_list, relx=40, max_width=35)

        self.nextrely += 1  # Move down
        self.add(AddFieldButton, name="Add Field", relx=40, max_width=13)
        self.add(CreateTableButton, name="Create Table", relx=40, max_width=13)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Enter in a name for a field (column) you would like to add to the new table. Choose a field " \
                   "type for the type of information you would like the field to contain, for example \"VARCHAR\" " \
                    "for text strings or  \"INT\" for integers. Add constraints as desired, for example " \
                   "\"REQUIRED\" means a row cannot be added with a blank entry for field, and \"PRIMARY KEY\" marks" \
                   "the data in this field as the primary key for references to this table. Finally, you can add " \
                   "additional fields as needed before creating the table, or if you're ready to create, choose " \
                   "\"CREATE TABLE\"."
        npyscreen.notify_confirm(help_msg, title='Help Menu')

    def on_ok(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")

    def on_cancel(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")


# More specifically, this is QuerySelectWindow, the default landing spot. TODO: Rename class and all references to it
class QueryWindow2(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit, action, selectBtn, insertBtn, \
    updateBtn, deleteBtn = (None,)*12
    # Data structure for managing user input for each table column
    queryData = {
        1: {
            'name': None,
            'field': {1: None,2:None,3:None},
            'filter': {
                1: {'operator': None,'field': None,'condition': None},
                2: {'operator': None,'field': None,'condition': None},
                3: {'operator': None,'field': None,'condition': None},
            },
            'sort': {'by': None,'order': None}
        },
        2: {'name': None,'field': {1: None,2:None,3:None},'filter': {
                1: {'operator': None,'field': None,'condition': None},
                2: {'operator': None,'field': None,'condition': None},
                3: {'operator': None,'field': None,'condition': None},}},
        3: {'name': None,'field': {1: None,2:None,3:None},
            'filter': {
                1: {'operator': None,'field': None,'condition': None},
                2: {'operator': None,'field': None,'condition': None},
                3: {'operator': None,'field': None,'condition': None},}}}



    def create(self):
        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45,
                                 color="VERYGOOD")
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        # Sub-nav for action type
        self.add(npyscreen.FixedText, value="Action: ", editable=False, relx=3, rely=3)
        self.nextrelx += 12
        self.nextrely -= 1
        self.selectBtn = self.add(QuerySelectBtn, name="SELECT", value="QueryWindow", color="VERYGOOD")
        self.nextrelx += 12
        self.nextrely -= 1
        self.insertBtn = self.add(QueryInsertBtn, name="INSERT", value="QueryInsertWindow")
        self.nextrelx += 12
        self.nextrely -= 1
        self.updateBtn = self.add(QueryUpdateBtn, name="UPDATE", value="QueryUpdateWindow")
        self.nextrelx += 12
        self.nextrely -= 1
        self.deleteBtn = self.add(QueryDeleteBtn, name="DELETE", value="QueryDeleteWindow")

        # Table 1
        self.nextrely += 1  # Move down
        self.nextrelx = 3  # Padding

        self.queryData[1]['name'] = self.add(npyscreen.TitleText, name="Table:", begin_entry_at=11, max_width=35)
        self.queryData[1]['field'][1] = self.add(npyscreen.TitleText, name="Field 1:", begin_entry_at=11, max_width=35)
        self.queryData[1]['field'][2] = self.add(npyscreen.TitleText, name="Field 2:", begin_entry_at=11, max_width=35)
        self.queryData[1]['field'][3] = self.add(npyscreen.TitleText, name="Field 3:", begin_entry_at=11, max_width=35)

        # Table 2
        self.nextrely -= 4  # Move up
        self.nextrelx += 36  # Move right

        self.queryData[2]['name'] = self.add(npyscreen.TitleText, name="Table:", begin_entry_at=11, max_width=35)
        self.queryData[2]['field'][1] = self.add(npyscreen.TitleText, name="Field 1:", begin_entry_at=11, max_width=35)
        self.queryData[2]['field'][2] = self.add(npyscreen.TitleText, name="Field 2:", begin_entry_at=11, max_width=35)
        self.queryData[2]['field'][3] = self.add(npyscreen.TitleText, name="Field 3:", begin_entry_at=11, max_width=35)

        # Table 3
        self.nextrely -= 4  # Move up
        self.nextrelx += 36  # Move right

        self.queryData[3]['name'] = self.add(npyscreen.TitleText, name="Table:", begin_entry_at=11, max_width=35)
        self.queryData[3]['field'][1] = self.add(npyscreen.TitleText, name="Field 1:", begin_entry_at=11, max_width=35)
        self.queryData[3]['field'][2] = self.add(npyscreen.TitleText, name="Field 2:", begin_entry_at=11, max_width=35)
        self.queryData[3]['field'][3] = self.add(npyscreen.TitleText, name="Field 3:", begin_entry_at=11, max_width=35)

        # CRITERIA/FILTER SECTION
        self.nextrely += 1  # Move down
        self.nextrelx = 3  # Add padding
        self.add(npyscreen.FixedText, value="Criteria: ", editable=False)

        # Table 1 criteria 1
        self.nextrelx = 3  # Add padding
        self.nextrely += 1 # Move down
        self.queryData[1]['filter'][1]['field'] = self.add(npyscreen.TitleText, name="Field:", begin_entry_at=13,
                                                           max_width=35)
        self.queryData[1]['filter'][1]['condition'] = self.add(npyscreen.TitleText, name="Condition:",
                                                               begin_entry_at=13, max_width=35)
        # Table 2 criteria 1
        self.nextrely -= 2  # Move up
        self.nextrelx += 36  # Move right
        self.queryData[2]['filter'][1]['field'] = self.add(npyscreen.TitleText, name="Field:", begin_entry_at=13,
                                                           max_width=35)
        self.queryData[2]['filter'][1]['condition'] = self.add(npyscreen.TitleText, name="Condition:",
                                                               begin_entry_at=13, max_width=35)
        # Table 3 criteria 1
        self.nextrely -= 2  # Move up
        self.nextrelx += 36  # Move right
        self.queryData[3]['filter'][1]['field'] = self.add(npyscreen.TitleText, name="Field:", begin_entry_at=13,
                                                           max_width=35)
        self.queryData[3]['filter'][1]['condition'] = self.add(npyscreen.TitleText, name="Condition:",
                                                               begin_entry_at=13, max_width=35)
        # CRITERIA OPERATORS ROW 1
        self.nextrelx = 3  # Add padding
        self.nextrely = 14 # Move down
        self.queryData[1]['filter'][1]['operator'] = self.add(npyscreen.SelectOne, max_height=2, value=[0],
                                                              values=["AND", "OR"], scroll_exit=True, max_width=35)
        self.nextrelx += 36  # Add padding
        self.nextrely -= 2 # Move up
        self.queryData[2]['filter'][1]['operator'] = self.add(npyscreen.SelectOne, max_height=2, value=[0],
                                                              values=["AND", "OR"], scroll_exit=True, max_width=35)
        self.nextrelx += 36  # Add padding
        self.nextrely -= 2 # Move up
        self.queryData[3]['filter'][1]['operator'] = self.add(npyscreen.SelectOne, max_height=2, value=[0],
                                                              values=["AND", "OR"], scroll_exit=True, max_width=35)
        # Table 1 criteria 2
        self.nextrelx = 3  # Add padding
        self.nextrely += 1 # Move down
        self.queryData[1]['filter'][2]['field'] = self.add(npyscreen.TitleText, name="Field:", begin_entry_at=13,
                                                           max_width=35)
        self.queryData[1]['filter'][2]['condition'] = self.add(npyscreen.TitleText, name="Condition:",
                                                               begin_entry_at=13, max_width=35)
        # Table 2 criteria 2
        self.nextrely -= 2  # Move up
        self.nextrelx += 36  # Move right
        self.queryData[2]['filter'][2]['field'] = self.add(npyscreen.TitleText, name="Field:", begin_entry_at=13,
                                                           max_width=35)
        self.queryData[2]['filter'][2]['condition'] = self.add(npyscreen.TitleText, name="Condition:",
                                                               begin_entry_at=13, max_width=35)
        # Table 3 criteria 2
        self.nextrely -= 2  # Move up
        self.nextrelx += 36  # Move right
        self.queryData[3]['filter'][2]['field'] = self.add(npyscreen.TitleText, name="Field:", begin_entry_at=13,
                                                           max_width=35)
        self.queryData[3]['filter'][2]['condition'] = self.add(npyscreen.TitleText, name="Condition:",
                                                               begin_entry_at=13, max_width=35)
        # CRITERIA OPERATORS ROW 2
        self.nextrelx = 3  # Add padding
        self.nextrely = 19 # Move down
        self.queryData[1]['filter'][2]['operator'] = self.add(npyscreen.SelectOne, max_height=2, value=[0],
                                                              values=["AND", "OR"], scroll_exit=True, max_width=35)
        self.nextrelx += 36  # Add padding
        self.nextrely -= 2 # Move up
        self.queryData[2]['filter'][2]['operator'] = self.add(npyscreen.SelectOne, max_height=2, value=[0],
                                                              values=["AND", "OR"], scroll_exit=True, max_width=35)
        self.nextrelx += 36  # Add padding
        self.nextrely -= 2 # Move up
        self.queryData[3]['filter'][2]['operator'] = self.add(npyscreen.SelectOne, max_height=2, value=[0],
                                                              values=["AND", "OR"], scroll_exit=True, max_width=35)
        # Table 1 criteria 3
        self.nextrelx = 3  # Add padding
        self.nextrely += 1 # Move down
        self.queryData[1]['filter'][3]['field'] = self.add(npyscreen.TitleText, name="Field:", begin_entry_at=13,
                                                           max_width=35)
        self.queryData[1]['filter'][3]['condition'] = self.add(npyscreen.TitleText, name="Condition:",
                                                               begin_entry_at=13, max_width=35)
        # Table 2 criteria 3
        self.nextrely -= 2  # Move up
        self.nextrelx += 36  # Move right
        self.queryData[2]['filter'][3]['field'] = self.add(npyscreen.TitleText, name="Field:", begin_entry_at=13,
                                                           max_width=35)
        self.queryData[2]['filter'][3]['condition'] = self.add(npyscreen.TitleText, name="Condition:",
                                                               begin_entry_at=13, max_width=35)
        # Table 3 criteria 3
        self.nextrely -= 2  # Move up
        self.nextrelx += 36  # Move right
        self.queryData[3]['filter'][3]['field'] = self.add(npyscreen.TitleText, name="Field:", begin_entry_at=13,
                                                           max_width=35)
        self.queryData[3]['filter'][3]['condition'] = self.add(npyscreen.TitleText, name="Condition:",
                                                               begin_entry_at=13, max_width=35)
        # Sorting
        self.nextrelx = 3  # Add padding
        self.nextrely += 1  # Move down

        self.queryData[1]['sort']['by'] = self.add(npyscreen.TitleText, name="Sort by:", begin_entry_at=11,
                                                   max_width=35)
        self.queryData[1]['sort']['order'] = self.add(npyscreen.SelectOne, max_height=2, value=[0], max_width=25,
                                                      values=["ASC", "DES"], scroll_exit=True)
        # QUERY PREVIEW - This will update to reflect the current form data
        self.nextrely -= 3  # Move up
        self.nextrelx = 39  # Move over
        self.add(npyscreen.FixedText, value="Preview: ", editable=False)
        self.queryPreview = self.add(npyscreen.FixedText, value="SELECT * FROM Customers WHERE Country='Mexico';",
                                     color="STANDOUT", editable=False)


        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use the SELECT form to query the database for stored data."
        npyscreen.notify_confirm(help_msg, title='Help Menu')

class QueryWindow(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit, action, selectBtn, insertBtn, \
    updateBtn, deleteBtn = (None,)*12
    # Data structure for managing user input for each table column

    def create(self):
        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45,
                                 color="VERYGOOD")
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        self.add(npyscreen.FixedText, value="Database: {}".format(self.parentApp.active_db), rely=3, relx=3,
                 color="LABEL", editable=False)

        # Sub-nav for action type

        self.selectBtn = self.add(QuerySelectBtn, name="SELECT", value="QueryWindow", color="VERYGOOD", rely=3, relx=37)

        self.insertBtn = self.add(QueryInsertBtn, name="INSERT", value="QueryInsertWindow", rely=3, relx=49)

        self.updateBtn = self.add(QueryUpdateBtn, name="UPDATE", value="QueryUpdateWindow", rely=3, relx=61)

        self.deleteBtn = self.add(QueryDeleteBtn, name="DELETE", value="QueryDeleteWindow", rely=3, relx=73)

        #label variables for selected table/fields
        self.lbl_table1_selected, self.lbl_table2_selected, self.lbl_table3_selected, self.lbl_field1_selected, \
        self.lbl_field2_selected, self.lbl_field3_selected = ("",)*6

        self.nextrely += 1  # Move down

        ''' TABLE 1 COLUMN '''
        self.nextrelx = 3  # Padding
        self.add(QB_TableBox01, name="Tables", values=self.parentApp.tableList, max_width=22, max_height=7,
                 scroll_exit=True)

        self.add(npyscreen.FixedText, w_id="wLabel_table1_selected", value="{}".format(self.lbl_table1_selected),
                 relx=4, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field_box1 = self.add(QB_FieldBox01, w_id="wField_list1", name="Fields", values=self.parentApp.field_list1,
                                   max_width=22, max_height=7, scroll_exit=True)

        self.add(npyscreen.FixedText, w_id="wLabel_field1_selected", value="{}".format(self.lbl_field1_selected),
                 relx=4, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.tbl1_criteria1 = self.add(npyscreen.TitleText, w_id="wTbl1_criteria1", name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.tbl1_condition1 = self.add(npyscreen.SelectOne, max_height=2, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.tbl1_criteria2 = self.add(npyscreen.TitleText, w_id="wTbl1_Criteria2", name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.tbl1_condition2 = self.add(npyscreen.SelectOne, max_height=2, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.tbl1_criteria3 = self.add(npyscreen.TitleText, w_id="wTbl1_Criteria3", name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 1  # Move down
        self.tbl1_sort = self.add(npyscreen.SelectOne, max_height=2, value=[0], max_width=10, values=["ASC", "DES"],
                                  scroll_exit=True)

        ''' TABLE 2 COLUMN '''
        self.nextrely = 5

        self.add(QB_TableBox02, name="Tables", values=self.parentApp.tableList, relx=30, max_width=22, max_height=7,
                 scroll_exit=True)

        self.add(npyscreen.FixedText, w_id="wLabel_table2_selected", value="{}".format(self.lbl_table2_selected),
                 relx=31, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field_box2 = self.add(QB_FieldBox02, w_id="wField_list2", name="Fields", values=self.parentApp.field_list2,
                                   relx=30, max_width=22, max_height=7, scroll_exit=True)

        self.add(npyscreen.FixedText, w_id="wLabel_field2_selected", value="{}".format(self.lbl_field2_selected),
                 relx=31, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.tbl2_criteria1 = self.add(npyscreen.TitleText, w_id="wCriteria1", relx=30, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.tbl2_condition1 = self.add(npyscreen.SelectOne, max_height=2, relx=30, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.tbl2_criteria2 = self.add(npyscreen.TitleText, w_id="wCriteria2", relx=30, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.tbl2_condition2 = self.add(npyscreen.SelectOne, max_height=2, relx=30, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.tbl2_criteria3 = self.add(npyscreen.TitleText, w_id="wCriteria3", relx=30, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 1  # Move down
        self.tbl2_sort = self.add(npyscreen.SelectOne, max_height=2, relx=30, value=[0], max_width=10,
                                  values=["ASC", "DES"], scroll_exit=True)

        ''' TABLE 3 COLUMN '''
        self.nextrely = 5

        self.add(QB_TableBox03, name="Tables", values=self.parentApp.tableList, relx=57, max_width=22, max_height=7,
                 scroll_exit=True)

        self.add(npyscreen.FixedText, w_id="wLabel_table3_selected", value="{}".format(self.lbl_table3_selected),
                 relx=58, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field_box3 = self.add(QB_FieldBox03, w_id="wField_list1", name="Fields", values=self.parentApp.field_list1,
                                   relx=57, max_width=22, max_height=7, scroll_exit=True)

        self.add(npyscreen.FixedText, w_id="wLabel_field3_selected", value="{}".format(self.lbl_field3_selected),
                 relx=58, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.tbl3_criteria1 = self.add(npyscreen.TitleText, w_id="wCriteria1", relx=57, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.tbl3_condition1 = self.add(npyscreen.SelectOne, max_height=2, relx=57, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.tbl3_criteria2 = self.add(npyscreen.TitleText, w_id="wCriteria2", relx=57, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.tbl3_condition2 = self.add(npyscreen.SelectOne, max_height=2, relx=57, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.tbl3_criteria3 = self.add(npyscreen.TitleText, w_id="wCriteria3", relx=57, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 1  # Move down
        self.tbl3_sort = self.add(npyscreen.SelectOne, max_height=2, relx=57, value=[0], max_width=10,
                                  values=["ASC", "DES"], scroll_exit=True)

        self.nextrely = 5
        self.add(Boxed_SQL_Query, name="SQL Query", w_id="wSQL_query", relx=84, max_height=22, max_width=33,
                 editable=True, scroll_exit=True)

        self.nextrely += 1
        self.add(QB_SQL_Build_Button, w_id="wSQL_Build_Button", relx=93, max_width=12, name="Build Query")
        self.nextrely += 1
        self.add(QB_SQL_Send_Button, w_id="wSQL_Send_Button", relx=93, max_width=12, name="Send Query")

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use the SELECT form to query the database for stored data."
        npyscreen.notify_confirm(help_msg, title='Help Menu')

class QueryInsertWindow(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit, action = (None,)*8

    def create(self):
        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        # Sub-nav for action type
        self.add(npyscreen.FixedText, value="Action: ", editable=False, relx=3, rely=3)
        self.nextrelx += 12
        self.nextrely -= 1
        self.selectBtn = self.add(QuerySelectBtn, name="SELECT", value="QueryWindow")
        self.nextrelx += 12
        self.nextrely -= 1
        self.insertBtn = self.add(QueryInsertBtn, name="INSERT", value="QueryInsertWindow", color="VERYGOOD")
        self.nextrelx += 12
        self.nextrely -= 1
        self.updateBtn = self.add(QueryUpdateBtn, name="UPDATE", value="QueryUpdateWindow")
        self.nextrelx += 12
        self.nextrely -= 1
        self.deleteBtn = self.add(QueryDeleteBtn, name="DELETE", value="QueryDeleteWindow")

        # DELETE THIS
        self.nextrely = 8
        self.nextrelx = 12
        self.add(npyscreen.FixedText, value="WELCOME TO THE INSERT FORM", editable=False)

        # Help menu guidance
        self.nextrely = 32
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use the INSERT form to add rows to the database."
        npyscreen.notify_confirm(help_msg, title='Help Menu')


class QueryUpdateWindow(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit, action = (None,)*8

    def create(self):
        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        # Sub-nav for action type
        self.add(npyscreen.FixedText, value="Action: ", editable=False, relx=3, rely=3)
        self.nextrelx += 12
        self.nextrely -= 1
        self.selectBtn = self.add(QuerySelectBtn, name="SELECT", value="QueryWindow")
        self.nextrelx += 12
        self.nextrely -= 1
        self.insertBtn = self.add(QueryInsertBtn, name="INSERT", value="QueryInsertWindow")
        self.nextrelx += 12
        self.nextrely -= 1
        self.updateBtn = self.add(QueryUpdateBtn, name="UPDATE", value="QueryUpdateWindow", color="VERYGOOD")
        self.nextrelx += 12
        self.nextrely -= 1
        self.deleteBtn = self.add(QueryDeleteBtn, name="DELETE", value="QueryDeleteWindow")

        # DELETE THIS
        self.nextrely = 8
        self.nextrelx = 12
        self.add(npyscreen.FixedText, value="WELCOME TO THE UPDATE FORM", editable=False)

        # Help menu guidance
        self.nextrely = 32
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use the UPDATE form to update a row in the database."
        npyscreen.notify_confirm(help_msg, title='Help Menu')


class QueryDeleteWindow(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit, action = (None,)*8

    def create(self):
        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        # Sub-nav for action type
        self.add(npyscreen.FixedText, value="Action: ", editable=False, relx=3, rely=3)
        self.nextrelx += 12
        self.nextrely -= 1
        self.selectBtn = self.add(QuerySelectBtn, name="SELECT", value="QueryWindow")
        self.nextrelx += 12
        self.nextrely -= 1
        self.insertBtn = self.add(QueryInsertBtn, name="INSERT", value="QueryInsertWindow")
        self.nextrelx += 12
        self.nextrely -= 1
        self.updateBtn = self.add(QueryUpdateBtn, name="UPDATE", value="QueryUpdateWindow")
        self.nextrelx += 12
        self.nextrely -= 1
        self.deleteBtn = self.add(QueryDeleteBtn, name="DELETE", value="QueryDeleteWindow", color="VERYGOOD")

        # DELETE THIS
        self.nextrely = 8
        self.nextrelx = 12
        self.add(npyscreen.FixedText, value="WELCOME TO THE DELETE FORM", editable=False)

        # Help menu guidance
        self.nextrely = 32
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use the DELETE form to delete rows from the database."
        npyscreen.notify_confirm(help_msg, title='Help Menu')


class QueryResultsWindow(npyscreen.ActionFormMinimal, npyscreen.SplitForm):

    def create(self):

        self.nextrely += 1  # Move down

        self.gridbox_results = self.add(Grid_Box_Results, max_height=27, values=self.parentApp.sql_results,
                                        default_column_number=10,
                                        contained_widget_arguments={"col_titles":self.parentApp.col_titles},
                                        col_margin=1, column_width=12,
                                        name="SQL Results")

        self.nextrely += 1  # Move down
        self.numrecords = self.add(npyscreen.FixedText, value="{} Records Found".format(self.parentApp.num_records),
                                   editable=False)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Query Builder results page. Select page navigation for viewing complete result. Scroll right to see" \
                   "extended columns."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def beforeEditing(self):

        self.gridbox_results.values = self.parentApp.sql_results

        self.gridbox_results.entry_widget.col_titles = self.parentApp.col_titles

        self.numrecords.value = "{} Records Found".format(self.parentApp.num_records)

        self.gridbox_results.display()
        self.numrecords.display()

    def on_ok(self):
        self.parentApp.switchForm("QueryWindow")


class RawSQLWindow(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = (None,)*7

    def create(self):
        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58, color="VERYGOOD")
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        self.nextrely += 1  # Move down

        self.add(Boxed_SQL_Query, name="Enter SQL Query", w_id="wSQL_query", max_height=7, editable=True,
                 scroll_exit=True)

        self.add(SQL_Send_Button, w_id="wSQL_Send_Button", relx=51, name="Send Query")

        self.nextrely += 2  # Move down

        self.nextrely += 1  # Move down
        self.gridbox_results = self.add(Grid_Box_Results, max_height=14, values=self.parentApp.sql_results,
                                        default_column_number=10,
                                        contained_widget_arguments={"col_titles":self.parentApp.col_titles},
                                        col_margin=1, column_width=12,
                                        name="SQL Results")

        self.nextrely += 1  # Move down
        self.numrecords = self.add(npyscreen.FixedText, value="{} Records Found".format(self.parentApp.num_records),
                                   editable=False)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use this page to enter and submit a raw SQL query without any of form assistance from the " \
                   "Query Builder or Tables pages. Entering raw SQL provides none of the protections that the " \
                   "aforementioned forms offer, and should only be performed by experienced users."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def beforeEditing(self):

        #clear grid widget results and num records on page load
        self.parentApp.col_titles = []
        self.gridbox_results.entry_widget.col_titles = self.parentApp.col_titles
        self.parentApp.sql_results = []
        self.gridbox_results.values = self.parentApp.sql_results
        self.gridbox_results.display()

        self.parentApp.num_records = 0
        self.numrecords.value = "{} Records Found".format(self.parentApp.num_records)
        self.numrecords.display()

class SQL_Query(npyscreen.MultiLineEdit):

    def display_value(self, vl):
        return


class Boxed_SQL_Query(npyscreen.BoxTitle):
    _contained_widget = SQL_Query


class Grid_Results(npyscreen.GridColTitles):

    def __init__(self, *args, **keywords):
        super(Grid_Results, self).__init__(*args, **keywords)


class Grid_Box_Results(npyscreen.BoxTitle):
    _contained_widget = Grid_Results


class QB_TableList01(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.get_widget("wLabel_table1_selected").value = "=> {}".format(act_on_this)
        self.parent.get_widget("wLabel_table1_selected").display()

        field_list = []

        #run query
        results = self.parent.parentApp.dbms.get_table_fields(act_on_this)
        if results[0] == "success":
            #npyscreen.notify_confirm("the results returned are :" + str(results[1]))
            for field in results[1]:
                field_list.append(field[0])
            self.parent.field_box1.values = field_list
            self.parent.field_box1.display()
            self.parent.parentApp.table1 = act_on_this

        else:
            npyscreen.notify_confirm(str(results[1]))

class QB_TableList02(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.get_widget("wLabel_table2_selected").value = "=> {}".format(act_on_this)
        self.parent.get_widget("wLabel_table2_selected").display()

        field_list = []

        #run query
        results = self.parent.parentApp.dbms.get_table_fields(act_on_this)
        if results[0] == "success":
            #npyscreen.notify_confirm("the results returned are :" + str(results[1]))
            for field in results[1]:
                field_list.append(field[0])
            self.parent.field_box2.values = field_list
            self.parent.field_box2.display()
            self.parent.parentApp.table1 = act_on_this

        else:
            npyscreen.notify_confirm(results[1])

class QB_TableList03(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.get_widget("wLabel_table3_selected").value = "=> {}".format(act_on_this)
        self.parent.get_widget("wLabel_table3_selected").display()

        field_list = []

        #run query
        results = self.parent.parentApp.dbms.get_table_fields(act_on_this)
        if results[0] == "success":
            #npyscreen.notify_confirm("the results returned are :" + str(results[1]))
            for field in results[1]:
                field_list.append(field[0])
            self.parent.field_box3.values = field_list
            self.parent.field_box3.display()
            self.parent.parentApp.table1 = act_on_this

        else:
            npyscreen.notify_confirm(results[1])

class QB_TableBox01(npyscreen.BoxTitle):
    _contained_widget = QB_TableList01

class QB_TableBox02(npyscreen.BoxTitle):
    _contained_widget = QB_TableList02

class QB_TableBox03(npyscreen.BoxTitle):
    _contained_widget = QB_TableList03


class QB_FieldList01(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):
        self.parent.get_widget("wLabel_field1_selected").value = "=> {}".format(act_on_this)
        self.parent.get_widget("wLabel_field1_selected").display()

        self.parent.parentApp.field1 = act_on_this

class QB_FieldList02(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):
        self.parent.get_widget("wLabel_field2_selected").value = "=> {}".format(act_on_this)
        self.parent.get_widget("wLabel_field2_selected").display()

        self.parent.parentApp.field2 = act_on_this

class QB_FieldList03(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):
        self.parent.get_widget("wLabel_field3_selected").value = "=> {}".format(act_on_this)
        self.parent.get_widget("wLabel_field3_selected").display()

        self.parent.parentApp.field3 = act_on_this


class QB_FieldBox01(npyscreen.BoxTitle):
    _contained_widget = QB_FieldList01

class QB_FieldBox02(npyscreen.BoxTitle):
    _contained_widget = QB_FieldList02

class QB_FieldBox03(npyscreen.BoxTitle):
    _contained_widget = QB_FieldList03


class ExportWindow(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = (None,)*7

    def create(self):
        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74, color="VERYGOOD")
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        self.add(npyscreen.FixedText, value="Here is the EXPORT window", editable=False)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use this page to export contents from a specified table to a CSV text file. This may be useful " \
                   "for importing database information to another program, such as Microsoft Excel."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)


class AdminWindow(npyscreen.ActionForm, npyscreen.SplitForm):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = (None,)*7

    def create(self):
        self.tabDatabases = self.add(TabMainButton, w_id="wMainTab", name="Main", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, relx=14, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=31)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=45)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=58)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=74)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=89,
                                 color="VERYGOOD")
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=103)

        self.add(npyscreen.FixedText, value="Here is the ADMIN window", editable=False)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use this screen to manage permissions for the currently selected database instance. You can add " \
                   "user accounts and modify user read/write access from this page."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)


class OpenDBButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.get_widget("wDatabases_box").value is None:
            npyscreen.notify_confirm("Please select a database by highlighting it and enter")
            return

        else:
            selected_db = self.parent.get_widget("wDatabases_box").values[self.parent.get_widget("wDatabases_box").value]
            self.parent.parentApp.active_db = selected_db
            self.parent.parentApp.dbms.connect_database(self.parent.parentApp.active_db)

            self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()

            self.parent.parentApp.switchForm("TablesWindow")


class CreateDBButton(npyscreen.ButtonPress):
    newDB_name = None

    def whenPressed(self):
        self.newDB_name = self.parent.get_widget("wNewDB_name").value
        create_confirm = npyscreen.notify_yes_no("Are you sure you want to create " + str(self.newDB_name) + "?",
                                                 "Confirm Creation", editw=2)
        if create_confirm:
            servermsg = self.parent.parentApp.dbms.create_database(self.newDB_name)
            npyscreen.notify_confirm(servermsg)
            self.parent.get_widget("wDatabases_box").values = self.parent.parentApp.dbms.list_databases()
            self.parent.get_widget("wDatabases_box").display()

            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class DeleteDBButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.get_widget("wDatabases_box").value is None:
            npyscreen.notify_confirm("Please select a database by highlighting it and enter")
            return

        else:
            selected_db = self.parent.get_widget("wDatabases_box").values[self.parent.get_widget("wDatabases_box").value]

            delete_confirm = npyscreen.notify_yes_no("Are you sure you want to delete " + str(selected_db) + "?",
                                                     "Confirm Deletion", editw=2)
            if delete_confirm:
                servermsg = self.parent.parentApp.dbms.delete_database(selected_db)
                npyscreen.notify_confirm(servermsg)
                self.parent.get_widget("wDatabases_box").values = self.parent.parentApp.dbms.list_databases()
                self.parent.get_widget("wDatabases_box").display()
                return

            else:
                npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class ViewTableStructButton(npyscreen.ButtonPress):
    selected_table, results = (None,)*2

    def whenPressed(self):
        if self.parent.get_widget("wTables_box").value is None:
            npyscreen.notify_confirm("Please select a table by highlighting it and enter")
            return
        else:
            self.selected_table = self.parent.parentApp.tableList[self.parent.get_widget("wTables_box").value]
            self.results = self.parent.parentApp.dbms.view_table_struct(self.selected_table)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))

        elif self.results[0] == 'success':
            self.parent.parentApp.table_results = self.results[1]
            if self.results[2]:
                self.parent.parentApp.col_titles = self.results[2]
            if self.results[3]:
                self.parent.parentApp.num_records = self.results[3]

            self.parent.gridbox_results.values = self.parent.parentApp.table_results

            self.parent.gridbox_results.entry_widget.col_titles = self.parent.parentApp.col_titles

            self.parent.numrecords.value = "{} Records Found".format(self.parent.parentApp.num_records)

            self.parent.gridbox_results.display()
            self.parent.numrecords.display()
            return


class BrowseTableButton(npyscreen.ButtonPress):
    selected_table, results = (None,)*2

    def whenPressed(self):
        if self.parent.get_widget("wTables_box").value is None:
            npyscreen.notify_confirm("Please select a table by highlighting it and enter")
            return
        else:
            self.selected_table = self.parent.parentApp.tableList[self.parent.get_widget("wTables_box").value]
            self.results = self.parent.parentApp.dbms.browse_table(self.selected_table)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))

        elif self.results[0] == 'success':
            self.parent.parentApp.table_results = self.results[1]
            if self.results[2]:
                self.parent.parentApp.col_titles = self.results[2]
            if self.results[3]:
                self.parent.parentApp.num_records = self.results[3]

            self.parent.gridbox_results.values = self.parent.parentApp.table_results

            self.parent.gridbox_results.entry_widget.col_titles = self.parent.parentApp.col_titles

            self.parent.numrecords.value = "{} Records Found".format(self.parent.parentApp.num_records)

            self.parent.gridbox_results.display()
            self.parent.numrecords.display()
            return


class BuildTableButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.get_widget("wNewTable_name").value == '':
            npyscreen.notify_confirm("Please enter the name of the table to be created first")
            return

        else:
            self.parent.parentApp.table_name = self.parent.get_widget("wNewTable_name").value

            if self.parent.parentApp.dbtype == 0:
                self.parent.parentApp.switchForm("TableCreatePostgreSQLForm")
            elif self.parent.parentApp.dbtype == 1:
                self.parent.parentApp.switchForm("TableCreateMySQLForm")


class AddFieldButton(npyscreen.ButtonPress):
    field_string, field_name, field_type, collation, constraint, not_null, default = (None,)*7

    def whenPressed(self):
        self.field_string = ""

        self.field_name = self.parent.get_widget("wField_name").value
        self.field_type = self.parent.get_widget("wField_type").get_selected_objects()[0]
        self.field_type_val = ""
        self.attribute = ""
        self.auto_increment = ""

        if self.parent.get_widget("wField_length_or_val").value:
            self.field_type_val += "("
            self.field_type_val += str(self.parent.get_widget("wField_length_or_val").value)
            self.field_type_val += ")"
            self.field_string += (self.field_name + " " + self.field_type + self.field_type_val)

        elif self.parent.parentApp.dbtype == 1 and self.field_type == "VARCHAR":
            npyscreen.notify_confirm("You must specify a length value for the VARCHAR data type")
            return

        else:
            self.field_string += (self.field_name + " " + self.field_type)

        if self.parent.parentApp.dbtype == 1:

            if self.parent.get_widget("wAttribute").get_selected_objects()[0] is not None:

                self.attribute = str(self.parent.get_widget("wAttribute").get_selected_objects()[0])

                if self.attribute == "binary" and (self.field_type != "tinytext" or "text" or "mediumtext" or "longtext"):

                    npyscreen.notify_confirm("The 'binary' attribute can only be used with one of the following data"
                                             " types:\ntinytext, text, mediumtext or longtext")
                    return

                elif (self.attribute == "unsigned" or self.attribute == "unsigned zerofill") \
                    and self.field_type not in ("TINYINT", "SMALLINT", "INT", "BIGINT", "FLOAT", "DOUBLE", "REAL",
                                                "DECIMAL", "NUMERIC"):

                    npyscreen.notify_confirm("The 'unsigned' and 'unsigned zerofill' attribute can only be used with"
                                             " one of the following data types:\n"
                                             "TINYINT, SMALLINT, INT, BIGINT, FLOAT, DOUBLE, REAL, DECIMAL or NUMERIC")
                    return

                elif self.attribute == "on update current_timestamp" and self.field_type != "TIMESTAMP":

                    npyscreen.notify_confirm("The 'on update current_timestamp' attribute can only be used with"
                                             " the TIMESTAMP data type")
                    return

                else:
                    self.field_string += (" " + self.attribute)

        if self.parent.get_widget("wCollation").get_selected_objects()[0] is not None:

            if self.parent.parentApp.dbtype == 0:

                if self.field_type not in ("CHAR", "VARCHAR", "TEXT"):
                    npyscreen.notify_confirm("Collation can only be used with CHAR, VARCHAR and TEXT data types")
                    return

                else:
                    #if postgreSQ, collation name needs double quotesL
                    self.collation = "COLLATE \"" + str(self.parent.get_widget("wCollation").get_selected_objects()[0])\
                                     + "\""

            else:

                if self.field_type not in ("CHAR", "VARCHAR", "TINYTEXT", "TEXT", "MEDIUMTEXT", "LONGTEXT"):
                    npyscreen.notify_confirm("Collation can only be used with CHAR, VARCHAR, TINYTEXT, TEXT,"
                                             " MEDIUMTEXT and LONGTEXT data types")
                    return

                else:
                    #if MySQL
                    self.collation = "COLLATE " + str(self.parent.get_widget("wCollation").get_selected_objects()[0])

            self.field_string += (" " + self.collation)

        if self.parent.get_widget("wConstraint").get_selected_objects()[0] is not None:

            self.constraint = self.parent.get_widget("wConstraint").get_selected_objects()[0]

        if self.parent.get_widget("wNot_null").value[0] == 1:
            self.not_null = "NOT NULL"

        elif self.parent.get_widget("wNot_null").value[0] == 0 and self.constraint != "PRIMARY KEY":
            self.not_null = "NULL"

        else:
            npyscreen.notify_confirm("A Primary Key cannot be null. Select the 'Required' option.")
            return

        self.field_string += (" " + self.not_null)

        if self.parent.get_widget("wDefault").value:
            self.default = "DEFAULT '" + str(self.parent.get_widget("wDefault").value) + "'"
            self.field_string += (" " + self.default)

        if self.parent.parentApp.dbtype == 1:

            if self.parent.get_widget("wAuto_increment").value[0] == 1 and self.field_type in ("TINYINT", "SMALLINT",
                                                    "INT", "BIGINT", "FLOAT", "DOUBLE", "REAL", "DECIMAL", "NUMERIC"):

                self.auto_increment = "AUTO_INCREMENT"
                self.field_string += (" " + self.auto_increment)

            elif self.parent.get_widget("wAuto_increment").value[0] == 1 and self.field_type not in ("TINYINT", "SMALLINT",
                                                    "INT", "BIGINT", "FLOAT", "DOUBLE", "REAL", "DECIMAL", "NUMERIC"):

                npyscreen.notify_confirm("Auto increment can only be used on a numeric data type")
                return

            self.parent.parentApp.engine = self.parent.get_widget("wStorage_engine").get_selected_objects()[0]

        if self.constraint:
            self.field_string += (" " + self.constraint)

        add_confirm = npyscreen.notify_yes_no("Add the following field?\n" + self.field_string, editw=2)
        if add_confirm:
            self.parent.parentApp.field_string_array.append(self.field_string + ", ")

            if self.parent.parentApp.dbtype == 0:
                self.parent.parentApp.switchForm("TableCreatePostgreSQLForm")

            else:
                self.parent.parentApp.switchForm("TableCreateMySQLForm")

        else:
            return


class CreateTableButton(npyscreen.ButtonPress):
    results = None

    def whenPressed(self):

        if self.parent.parentApp.dbtype == 1 and not self.parent.parentApp.field_string_array:
                npyscreen.notify_confirm("Sorry, you can't create an empty table in MySQL")
                return

        create_confirm = npyscreen.notify_yes_no("Are you sure you want to create " +
                                                 str(self.parent.parentApp.table_name) + "?", "Confirm Creation",
                                                 editw=2)

        if create_confirm:
            create_table_string = "CREATE TABLE {} ".format(self.parent.parentApp.table_name)
            field_string = ""

            if self.parent.parentApp.field_string_array is not None:
                for field in self.parent.parentApp.field_string_array:
                    field_string += field
                field_string = field_string[:-2]

            create_table_string += "(" + field_string + ")"

            if self.parent.parentApp.dbtype == 1:
                create_table_string += "ENGINE=" + self.parent.parentApp.engine + ";"

            npyscreen.notify_confirm(create_table_string)

            self.results = self.parent.parentApp.dbms.execute_SQL(create_table_string)

            if self.results[0] == 'error':
                if self.results[1] == 'no results to fetch':
                    npyscreen.notify_confirm("Table {} successfully created".format(self.parent.parentApp.table_name))

                else:
                    npyscreen.notify_confirm(str(self.results[1]))
                    self.parent.parentApp.field_string_array = []
                    return

            elif self.results[0] == 'success':
                npyscreen.notify_confirm("Table {} successfully created".format(self.parent.parentApp.table_name))

            self.parent.parentApp.field_string_array = []
            self.parent.parentApp.table_results = []
            self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()

            self.parent.parentApp.switchForm("TablesWindow")

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class DeleteTableButton(npyscreen.ButtonPress):
    selected_table = None

    def whenPressed(self):
        if self.parent.get_widget("wTables_box").value is None:
            npyscreen.notify_confirm("Please select a table by highlighting it and enter")
            return
        else:
            self.selected_table = self.parent.parentApp.tableList[self.parent.get_widget("wTables_box").value]

        delete_confirm = npyscreen.notify_yes_no("Are you sure you want to delete " + str(self.selected_table) + "?",
                                                 "Confirm Deletion", editw=2)
        if delete_confirm:
            servermsg = self.parent.parentApp.dbms.delete_table(self.selected_table)
            if servermsg:
                npyscreen.notify_confirm(servermsg)

            self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()
            self.parent.get_widget("wTables_box").values = self.parent.parentApp.tableList
            self.parent.get_widget("wTables_box").display()
            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form

class QB_SQL_Build_Button(npyscreen.ButtonPress):
    sql_command, results = (None,)*2

    def whenPressed(self):
        pass

class QB_SQL_Send_Button(npyscreen.ButtonPress):
    sql_command, results = (None,)*2

    def whenPressed(self):

        #clear results
        self.parent.parentApp.sql_results = []
        self.parent.parentApp.col_titles = []

        self.sql_query = self.parent.get_widget("wSQL_query").value
        self.results = self.parent.parentApp.dbms.execute_SQL(self.sql_query)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))
            return

        elif self.results[0] == 'success':

            self.parent.parentApp.sql_results = self.results[1]
            if self.results[2]:
                self.parent.parentApp.col_titles = self.results[2]
            if self.results[3]:
                self.parent.parentApp.num_records = self.results[3]

            self.parent.parentApp.switchForm("QueryResultsWindow")

class SQL_Send_Button(npyscreen.ButtonPress):
    sql_command, results = (None,)*2

    def whenPressed(self):

        #clear results
        self.parent.parentApp.sql_results = []
        self.parent.parentApp.col_titles = []

        self.sql_query = self.parent.get_widget("wSQL_query").value
        self.results = self.parent.parentApp.dbms.execute_SQL(self.sql_query)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))
            return

        elif self.results[0] == 'success':

            self.parent.parentApp.sql_results = self.results[1]
            if self.results[2]:
                self.parent.parentApp.col_titles = self.results[2]
            if self.results[3]:
                self.parent.parentApp.num_records = self.results[3]

            self.parent.gridbox_results.values = self.parent.parentApp.sql_results

            self.parent.gridbox_results.entry_widget.col_titles = self.parent.parentApp.col_titles

            self.parent.numrecords.value = "{} Records Found".format(self.parent.parentApp.num_records)

            self.parent.gridbox_results.display()
            self.parent.numrecords.display()
            return


class QuerySelectBtn(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryWindow")
        return


class QueryInsertBtn(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryInsertWindow")
        return


class QueryUpdateBtn(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryUpdateWindow")
        return


class QueryDeleteBtn(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryDeleteWindow")
        return

'''NAV BAR BUTTONS'''
class TabMainButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("MAIN")
        return

class TabDatabaseButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("DatabaseWindow")
        return

class TabTablesButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.parentApp.active_db is None:
            npyscreen.notify_confirm("You must first open a database before accessing the Tables page")
            return

        else:
            self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()
            self.parent.parentApp.switchForm("TablesWindow")

class TabQueryButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.parentApp.active_db is None:
            npyscreen.notify_confirm("You must first open a database before accessing the Query Builder page")
            return

        else:
            self.parent.parentApp.switchForm("QueryWindow")


class TabQuery2Button(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryWindow2")
        return

class TabRawSQLButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("RawSQLWindow")
        return

class TabExportButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("ExportWindow")
        return

class TabAdminButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("AdminWindow")
        return

class ExitButton(npyscreen.ButtonPress):
    def whenPressed(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=2)
        if exiting:
            self.parent.parentApp.switchForm(None)
        else:
            # Clears the notification and just goes back to the original form
            npyscreen.blank_terminal()
        return

#for testing
class Nav_Bar(npyscreen.Form):

    def create(self):

            self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                 rely=1, max_height=1, scroll_exit=True)
            self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                      relx=15, max_height=1)
            self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1,
                                     relx=25, max_height=1)
            self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                      relx=34, max_height=1)
            self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                      relx=45, max_height=1)
            self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1,
                                     relx=55, max_height=1)
            self.add(ExitButton, name="Exit", rely=1, relx=64, max_height=1)


# NPSAppManaged provides a framework to start and end the application
# Manages the display of the various Forms we have created
class App(npyscreen.NPSAppManaged):

    dbtype, host, port, username, password, dbms, active_db, tableList, active_table = (None,)*9

    # Table creation global variables
    field_name, field_type, field_length_or_val, field_collation, field_attrib, field_default = (None,)*6

    engine = "InnoDB" #sets default MySQL engine type

    field_autoincrement, field_primarykey, field_unique, field_index = (False,)*4
    # User friendly way of saying if Null is okay for this field
    field_optional = True

    field1, field2, field3, tbl1_criteria1, tbl1_criteria2, tbl1_criteria3, tbl2_criteria1, tbl2_criteria2, \
    tbl2_criteria3, tbl3_criteria1, tbl3_criteria2, tbl3_criteria3, table1, table2, table3 = (None,)*15

    tablefield_cols, sql_results, col_titles, table_results, table_struct_results, field_string_array, field_list1,\
        field_list2, field_list3 = ([],)*9

    num_records = 0

    def onStart(self):

        # Declare all the forms that will be used within the app
        self.addFormClass("MAIN", Initial, name="Welcome to ezdb", draw_line_at=34)
        self.addFormClass("ConnectDBMS", ConnectDBMS, name="ezdb >> DBMS Connection Page", draw_line_at=34)
        self.addFormClass("DatabaseWindow", DatabaseWindow, name="ezdb >> Database Page", draw_line_at=34)
        self.addFormClass("TablesWindow", TablesWindow, name="ezdb >> Tables Page", draw_line_at=34)
        self.addFormClass("QueryWindow", QueryWindow, name="ezdb >> Query >> SELECT Page", draw_line_at=34)
        self.addFormClass("QueryWindow2", QueryWindow2, name="ezdb >> Query >> SELECT Page", draw_line_at=34)
        self.addFormClass("QueryInsertWindow", QueryInsertWindow, name="ezdb >> Query >> INSERT Page", draw_line_at=34)
        self.addFormClass("QueryUpdateWindow", QueryUpdateWindow, name="ezdb >> Query >> UPDATE Page", draw_line_at=34)
        self.addFormClass("QueryDeleteWindow", QueryDeleteWindow, name="ezdb >> Query >> DELETE Page", draw_line_at=34)
        self.addFormClass("QueryResultsWindow", QueryResultsWindow, name="ezdb >> Query >> Results Page", draw_line_at=34)
        self.addFormClass("RawSQLWindow", RawSQLWindow, name="ezdb >> Raw SQL Page", draw_line_at=34)
        self.addFormClass("ExportWindow", ExportWindow, name="ezdb >> Export Page", draw_line_at=34)
        self.addFormClass("AdminWindow", AdminWindow, name="ezdb >> Admin Page", draw_line_at=34)
        self.addFormClass("TableCreatePostgreSQLForm", TableCreatePostgreSQLForm, name="ezdb >> Build/Create Table",
                          draw_line_at=34)
        self.addFormClass("TableCreateMySQLForm", TableCreateMySQLForm, name="ezdb >> Build/Create Table",
                          draw_line_at=34)
        # for testing:
        # self.addForm("Nav_Bar", Nav_Bar)

if __name__ == "__main__":

    print "Resizing terminal..."

    #resizes the terminal to 120 x 35
    print "\x1b[8;37;120t"

    #necessary pause to prevent race condition and allow termnal time to resize before launching npyscreen form
    time.sleep(1)

    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()