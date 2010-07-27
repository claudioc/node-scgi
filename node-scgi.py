"""
A SCGI handler to test node.js scgi module.
Code inherited from the Quixote scgi-server example
"""

import sys
import time
import os
import getopt
import signal
import scgi_server

pidfilename = None # set by main()

def debug(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S",
                              time.localtime(time.time()))
    sys.stderr.write("[%s] %s\n" % (timestamp, msg))

class NodeScgiHandler(scgi_server.SCGIHandler):

    def __init__(self, *args, **kwargs):
        debug("%s created" % self.__class__.__name__)
        scgi_server.SCGIHandler.__init__(self, *args, **kwargs)

    def handle_connection (self, conn):
        input = conn.makefile("r")
        output = conn.makefile("w")

        env = self.read_env(input)

        output.write("Status: 200 OK\r\n")
        output.write("Content-Type: text/html\r\n")
        
        #body = "Hello!\n" + env['SCRIPT_NAME'] + "\n" + env['QUERY_STRING'] + "\n" + env['HTTP_USER_AGENT'] + "\n" + env['HTTP_ACCEPT'] + "\n" + env['HTTP_HOST'] + "\n" + env['HTTP_CONNECTION'] + "\n" + env['REQUEST_URI'] + "\n" + env['REQUEST_METHOD']

        body = "<html><head></head><body><strong>Yes, it works.</strong>OK?</body></html>"

        output.write("Content-Length: " + str(len(body)) + "\r\n")
        
        output.write("\r\n")

        output.write(body)
        
        try:
            input.close()
            output.close()
            conn.close()
        except IOError, err:
            debug("IOError while closing connection ignored: %s" % err)


def change_uid_gid(uid, gid=None):
    "Try to change UID and GID to the provided values"
    # This will only work if this script is run by root.

    # Try to convert uid and gid to integers, in case they're numeric
    import pwd, grp
    try:
        uid = int(uid)
        default_grp = pwd.getpwuid(uid)[3]
    except ValueError:
        uid, default_grp = pwd.getpwnam(uid)[2:4]

    if gid is None:
        gid = default_grp
    else:
        try:
            gid = int(gid)
        except ValueError:
            gid = grp.getgrnam(gid)[2]

    os.setgid(gid)
    os.setuid(uid)


def term_signal(signum, frame):
    global pidfilename
    try:
        os.unlink(pidfilename)
    except OSError:
        pass
    sys.exit()

class MyHandler(NodeScgiHandler):

    def __init__(self, *args, **kwargs):
        NodeScgiHandler.__init__(self, *args, **kwargs)

def main(h=MyHandler):
  
    usage = """Usage: %s [options]
    
    -F -- stay in foreground (don't fork)
    -P -- PID filename
    -l -- log filename
    -m -- max children
    -p -- TCP port to listen on
    -u -- user id to run under
    """ % sys.argv[0]
    nofork = 0
    global pidfilename
    pidfilename = "/var/tmp/node-scgi.pid"
    logfilename = "/var/tmp/node-scgi.log"
    max_children = 5    # scgi default
    uid = "nobody"
    port = 4000
    host = "127.0.0.1"
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'FP:l:m:p:u:')
    except getopt.GetoptError, exc:
        print >>sys.stderr, exc
        print >>sys.stderr, usage
        sys.exit(1)
    for o, v in opts:
        if o == "-F":
            nofork = 1
        elif o == "-P":
            pidfilename = v
        elif o == "-l":
            logfilename = v
        elif o == "-m":
            max_children = int(v)
        elif o == "-p":
            port = int(v)
        elif o == "-u":
            uid = v

    log = open(logfilename, "a", 1)
    os.dup2(log.fileno(), 1)
    os.dup2(log.fileno(), 2)
    os.close(0)

    if os.getuid() == 0:
        change_uid_gid(uid)

    if nofork:
        scgi_server.SCGIServer(h, host=host, port=port,
                               max_children=max_children).serve()
    else:
        pid = os.fork()
        if pid == 0:
            pid = os.getpid()
            pidfile = open(pidfilename, 'w')
            pidfile.write(str(pid))
            pidfile.close()
            signal.signal(signal.SIGTERM, term_signal)
            try:
                scgi_server.SCGIServer(h, host=host, port=port,
                                       max_children=max_children).serve()
            finally:
                # grandchildren get here too, don't let them unlink the pid
                if pid == os.getpid():
                    try:
                        os.unlink(pidfilename)
                    except OSError:
                        pass

if __name__ == '__main__':
    main()

