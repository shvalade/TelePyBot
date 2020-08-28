import mariadb
import logging
import config
import time
import urllib3
from bs4 import BeautifulSoup
import certifi

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config.loggingLevel)
logger = logging.getLogger('master')


class SQLighter:

    def __init__(self, user, passwd, db):
        """connect to db, save cursor"""
        self.user = user
        self.password = passwd
        self.database = db
        self._connection = None
        self._cursor = None
        # self._connection = None
        # print(self.connection)
        # self._cursor = self.connection.cursor()
        # print(self.cursor.__dict__)
        # self._cursor.execute("SELECT * FROM `subs` WHERE `status` = ?", (True,))
        # print(self._cursor.fetchall())

    def connect(self):
        self._connection = mariadb.connect(db=self.database, user=self.user, passwd=self.password)
        self._cursor = self._connection.cursor()

    def disconnect(self):
        self._connection.close()

    def execute_queue(self, queue, params=None):
        # for i in range(10):
        #     str = i, ' Wait a moment! ', params.__dict__
        #     logger.debug(str)
        #     time.sleep(1)
        self._cursor.execute(queue, params)

    def commit(self):
        return self._connection.commit()

    def fetch_all(self):
        return self._cursor.fetchall()

    def fetch_one(self):
        return self._cursor.fetchone()

    def select_all(self):
        self.connect()
        self.execute_queue("select `link`, `title` from actual_songs")
        # test = (('', '',), ('', ''))
        # test.
        res = ''.join(map(lambda x: str('\n'.join(map(str, x)) + '\n\n'), self.fetch_all()))
        self.disconnect()
        return res

    def get_subscription(self, status=True):
        """get all active users"""
        self.connect()
        self.execute_queue("SELECT * FROM `subs` WHERE `status` = ?", (status,))
        res = self.fetch_all()
        self.disconnect()
        return res

    def get_user_status(self, user_id):
        self.connect()
        self.execute_queue("SELECT `status` FROM `subs` where `user_id` = ?", (user_id,))
        res = self.fetch_one()
        print(res[0])
        self.disconnect()
        return res[0]

    def subscriber_exist(self, user_id):
        """check if user already in DB"""
        self.connect()
        self.execute_queue("SELECT * FROM `subs` WHERE `user_id` = ?", (user_id,))
        result = self.fetch_all()
        self.disconnect()
        return bool(len(result))

    def add_subscriber(self, user_id, status=True):
        """add new subs"""
        self.connect()
        self.execute_queue("INSERT INTO `subs` (`user_id`, `status`) VALUES (?,?)", (user_id, status))
        self.commit()
        self.disconnect()

    def update_subscription(self, user_id, status):
        """update user sub-status"""
        self.connect()
        self.execute_queue("UPDATE `subs` SET `status` = ? WHERE `user_id` = ?", (status, user_id))
        self.commit()
        self.disconnect()
        return

    def get_random_song(self):
        self.connect()
        self.execute_queue("SELECT `user_id`, `link` FROM `actual_songs` ORDER BY RAND() LIMIT 1")
        res = self.fetch_one()
        self.disconnect()
        return res

    def push_song(self, user_id, link):
        self.connect()
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        r = http.request('GET', link)
        soup = BeautifulSoup(r.data, 'html.parser')
        self._cursor.execute("INSERT INTO `actual_songs` (`link`, `title`, `user_id`) VALUES (?, ?, ?)", (link,  soup.title.string, user_id,))
        self.commit()
        self.disconnect()

    def get_rotate_random_song(self):
        self.connect()
        self.execute_queue("SELECT * FROM `actual_songs` ORDER BY RAND() LIMIT 1")
        res = self.fetch_one()
        logger.debug(res)
        id = res[0]
        create_timestamp = res[1]
        last_access = res[2]
        link = res[3]
        title = res[4]
        user_id = res[5]
        rotate = time.strftime('%Y-%m-%d %H:%M:%S')
        self.execute_queue("DELETE FROM `actual_songs` WHERE `id` = ?", (id,))

        self.execute_queue(f"INSERT INTO `old_songs` "
                           f"(`actual_song_id`, `create_timestamp`, `last_access`, `rotate_timestamp`, `link`, `title`) "
                           f"VALUES (?, ?, ?, ?, ?, ?)", (id, create_timestamp, last_access, rotate, link, title,))
        self.commit()
        self.disconnect()
        return res[0], res[3]

    def get_user_songs(self, usr_id):
        self.connect()
        self.execute_queue("SELECT `link`, `title` FROM `actual_songs` WHERE `user_id` = ?", (usr_id,))
        # res = self.fetch_all()
        res = ''.join(map(lambda x: str('\n'.join(map(str, x)) + '\n\n'), self.fetch_all()))
        self.disconnect()
        return res
