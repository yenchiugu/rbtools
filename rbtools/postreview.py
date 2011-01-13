import base64
    # Specifically import json_loads, to work around some issues with
    # installations containing incompatible modules named "json".
    from json import loads as json_loads
    from simplejson import loads as json_loads
from rbtools import get_package_version, get_version_string


ADD_REPOSITORY_DOCS_URL = \
    'http://www.reviewboard.org/docs/manual/dev/admin/management/repositories/'
GNU_DIFF_WIN32_URL = 'http://gnuwin32.sourceforge.net/packages/diffutils.htm'

    def __init__(self, http_status, error_code, rsp=None, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.http_status = http_status
        self.error_code = error_code
        self.rsp = rsp

    def __str__(self):
        code_str = "HTTP %d" % self.http_status

        if self.error_code:
            code_str += ', API Error %d' % self.error_code

        if self.rsp and 'err' in self.rsp:
            return '%s (%s)' % (self.rsp['err']['msg'], code_str)
        else:
            return code_str


class HTTPRequest(urllib2.Request):
    def __init__(self, url, body, headers={}, method="PUT"):
        urllib2.Request.__init__(self, url, body, headers)
        self.method = method

    def get_method(self):
        return self.method
            if e.error_code == 210:
class PresetHTTPAuthHandler(urllib2.BaseHandler):
    """urllib2 handler that conditionally presets the use of HTTP Basic Auth.

    This is used when specifying --username= on the command line. It will
    force an HTTP_AUTHORIZATION header with the user info, asking the user
    for any missing info beforehand. It will then try this header for that
    first request.

    It will only do this once.
    """
    handler_order = 480 # After Basic auth

    def __init__(self, url, password_mgr):
        self.url = url
        self.password_mgr = password_mgr
        self.used = False

    def reset(self):
        self.password_mgr.rb_user = None
        self.password_mgr.rb_pass = None
        self.used = False

    def http_request(self, request):
        if options.username and not self.used:
            # Note that we call password_mgr.find_user_password to get the
            # username and password we're working with. This allows us to
            # prompt if, say, --username was specified but --password was not.
            username, password = \
                self.password_mgr.find_user_password('Web API', self.url)
            raw = '%s:%s' % (username, password)
            request.add_header(
                urllib2.HTTPBasicAuthHandler.auth_header,
                'Basic %s' % base64.b64encode(raw).strip())
            self.used = True

        return request

    https_request = http_request


class ReviewBoardHTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    """Processes HTTP error codes.

    Python 2.6 gets HTTP error code processing right, but 2.4 and 2.5 only
    accepts HTTP 200 and 206 as success codes. This handler ensures that
    anything in the 200 range is a success.
    """
    def http_response(self, request, response):
        if not (200 <= response.code < 300):
            response = self.parent.error('http', request, response,
                                         response.code, response.msg,
                                         response.info())

        return response

    https_response = http_response


class ReviewBoardHTTPBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
    """Custom Basic Auth handler that doesn't retry excessively.

    urllib2's HTTPBasicAuthHandler retries over and over, which is useless.
    This subclass only retries once to make sure we've attempted with a
    valid username and password. It will then fail so we can use
    tempt_fate's retry handler.
    """
    def __init__(self, *args, **kwargs):
        urllib2.HTTPBasicAuthHandler.__init__(self, *args, **kwargs)
        self._retried = False

    def retry_http_basic_auth(self, *args, **kwargs):
        if not self._retried:
            self._retried = True
            response = urllib2.HTTPBasicAuthHandler.retry_http_basic_auth(
                self, *args, **kwargs)

            if response.code != 401:
                self._retried = False

            return response
        else:
            return None


    def __init__(self, reviewboard_url, rb_user=None, rb_pass=None):
        self.rb_user = rb_user
        self.rb_pass = rb_pass
                if options.diff_filename == '-':
                    die('HTTP authentication is required, but cannot be '
                        'used with --diff-filename=-')

                print 'Enter authorization information for "%s" at %s' % \

                if not self.rb_user:
                    self.rb_user = raw_input('Username: ')

                if not self.rb_pass:
                    self.rb_pass = getpass.getpass('Password: ')
        self.root_resource = None
        self.deprecated_api = False
        try:
            self.cookie_jar.load(self.cookie_file, ignore_expires=True)
        except IOError:
            pass
        cookie_handler      = urllib2.HTTPCookieProcessor(self.cookie_jar)
        password_mgr        = ReviewBoardHTTPPasswordMgr(self.url,
                                                         options.username,
                                                         options.password)
        basic_auth_handler  = ReviewBoardHTTPBasicAuthHandler(password_mgr)
        digest_auth_handler = urllib2.HTTPDigestAuthHandler(password_mgr)
        self.preset_auth_handler = PresetHTTPAuthHandler(self.url, password_mgr)
        http_error_processor = ReviewBoardHTTPErrorProcessor()

        opener = urllib2.build_opener(cookie_handler,
                                      basic_auth_handler,
                                      digest_auth_handler,
                                      self.preset_auth_handler,
                                      http_error_processor)
        opener.addheaders = [('User-agent', 'RBTools/' + get_package_version())]
    def check_api_version(self):
        """Checks the API version on the server to determine which to use."""
        try:
            rsp = self.api_get('api/')
            self.deprecated_api = False
            self.root_resource = rsp
            debug('Using the new web API')
        except APIError, e:
            if e.http_status == 404:
                # This is an older Review Board server with the old API.
                self.deprecated_api = True
                debug('Using the deprecated Review Board 1.0 web API')
            else:
                # We shouldn't reach this. If there's a permission denied
                # from lack of logging in, then the basic auth handler
                # should have hit it.
                die("Unable to access the root /api/ URL on the server.")

        if not self.root_resource:
            self.check_api_version()

        if (options.diff_filename == '-' and
            not options.username and not options.submit_as and
            not options.password):
            die('Authentication information needs to be provided on '
                'the command line when using --diff-filename=-')

        if self.deprecated_api:
            print "==> Review Board Login Required"
            print "Enter username and password for Review Board at %s" % \
                  self.url

            if options.username:
                username = options.username
            elif options.submit_as:
                username = options.submit_as
            elif not force and self.has_valid_cookie():
                # We delay the check for a valid cookie until after looking
                # at args, so that it doesn't override the command line.
                return
            else:
                username = raw_input('Username: ')
            if not options.password:
                password = getpass.getpass('Password: ')
            else:
                password = options.password
            debug('Logging in with username "%s"' % username)
            try:
                self.api_post('api/json/accounts/login/', {
                    'username': username,
                    'password': password,
                })
            except APIError, e:
                die("Unable to log in: %s" % e)
            debug("Logged in.")
        elif force:
            self.preset_auth_handler.reset()
            # Cookie files also append .local to bare hostnames
            if '.' not in host:
                host += '.local'


        # If repository_path is a list, find a name in the list that's
        # registered on the server.
        if isinstance(self.info.path, list):
            repositories = self.get_repositories()

            debug("Repositories on Server: %s" % repositories)
            debug("Server Aliases: %s" % self.info.path)

            for repository in repositories:
                if repository['path'] in self.info.path:
                    self.info.path = repository['path']
                    break

            debug("Attempting to create review request on %s for %s" %
                  (self.info.path, changenum))
            data = {}
            if self.deprecated_api:
                data['repository_path'] = self.info.path
                rsp = self.api_post('api/json/reviewrequests/new/', data)
            else:
                data['repository'] = self.info.path

                links = self.root_resource['links']
                assert 'review_requests' in links
                review_request_href = links['review_requests']['href']
                rsp = self.api_post(review_request_href, data)
            if e.error_code == 204: # Change number in use
                rsp = e.rsp
                if options.diff_only:
                    # In this case, fall through and return to tempt_fate.
                    debug("Review request already exists.")
                    debug("Review request already exists. Updating it...")
                    self.update_review_request_from_changenum(
                        changenum, rsp['review_request'])
            elif e.error_code == 206: # Invalid repository
                sys.stderr.write('\n')
                sys.stderr.write('There was an error creating this review '
                                 'request.\n')
                sys.stderr.write('\n')
                sys.stderr.write('The repository path "%s" is not in the\n' %
                                 self.info.path)
                sys.stderr.write('list of known repositories on the server.\n')
                sys.stderr.write('\n')
                sys.stderr.write('Ask the administrator to add this '
                                 'repository to the Review Board server.\n')
                sys.stderr.write('For information on adding repositories, '
                                 'please read\n')
                sys.stderr.write(ADD_REPOSITORY_DOCS_URL + '\n')
                die()
            else:
                raise e
        else:
            debug("Review request created")
    def update_review_request_from_changenum(self, changenum, review_request):
        if self.deprecated_api:
            rsp = self.api_post(
                'api/json/reviewrequests/%s/update_from_changenum/'
                % review_request['id'])
        else:
            rsp = self.api_put(review_request['links']['self']['href'], {
                'changenum': review_request['changenum'],
            })

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/draft/set/' % rid, {
                field: value,
            })
        else:
            self.api_put(review_request['links']['draft']['href'], {
                field: value,
            })
        if self.deprecated_api:
            url = 'api/json/reviewrequests/%s/'
        else:
            url = '%s%s/' % (
                self.root_resource['links']['review_requests']['href'], rid)

        rsp = self.api_get(url)

        if self.deprecated_api:
            rsp = self.api_get('api/json/repositories/')
            repositories = rsp['repositories']
        else:
            rsp = self.api_get(
                self.root_resource['links']['repositories']['href'])
            repositories = rsp['repositories']

            while 'next' in rsp['links']:
                rsp = self.api_get(rsp['links']['next']['href'])
                repositories.extend(rsp['repositories'])

        return repositories
        if self.deprecated_api:
            url = 'api/json/repositories/%s/info/' % rid
        else:
            rsp = self.api_get(
                '%s%s/' % (self.root_resource['links']['repositories']['href'],
                           rid))
            url = rsp['repository']['links']['info']['href']

        rsp = self.api_get(url)

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/draft/save/' % \
                          review_request['id'])
        else:
            self.api_put(review_request['links']['draft']['href'], {
                'public': 1,
            })

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/diff/new/' %
                          review_request['id'], fields, files)
        else:
            self.api_post(review_request['links']['diffs']['href'],
                          fields, files)

    def reopen(self, review_request):
        """
        Reopen discarded review request.
        """
        debug("Reopening")

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/reopen/' %
                          review_request['id'])
        else:
            self.api_put(review_request['links']['self']['href'], {
                'status': 'pending',
            })

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/publish/' %
                          review_request['id'])
        else:
            self.api_put(review_request['links']['draft']['href'], {
                'public': 1,
            })
        rsp = json_loads(data)
            # With the new API, we should get something other than HTTP
            # 200 for errors, in which case we wouldn't get this far.
            assert self.deprecated_api
            self.process_error(200, data)
    def process_error(self, http_status, data):
        """Processes an error, raising an APIError with the information."""
        try:
            rsp = json_loads(data)

            assert rsp['stat'] == 'fail'

            debug("Got API Error %d (HTTP code %d): %s" %
                  (rsp['err']['code'], http_status, rsp['err']['msg']))
            debug("Error data: %r" % rsp)
            raise APIError(http_status, rsp['err']['code'], rsp,
                           rsp['err']['msg'])
        except ValueError:
            debug("Got HTTP error: %s: %s" % (http_status, data))
            raise APIError(http_status, None, None, data)

        rsp = urllib2.urlopen(url).read()
        except IOError, e:
            debug('Failed to write cookie file: %s' % e)
        return rsp
        if path.startswith('http'):
            # This is already a full path.
            return path


        try:
            return self.process_json(self.http_get(path))
        except urllib2.HTTPError, e:
            self.process_error(e.code, e.read())
            try:
                self.cookie_jar.save(self.cookie_file)
            except IOError, e:
                debug('Failed to write cookie file: %s' % e)
            return data
        except urllib2.HTTPError, e:
            # Re-raise so callers can interpret it.
            raise e
        except urllib2.URLError, e:
            try:
                debug(e.read())
            except AttributeError:
                pass

            die("Unable to access %s. The host path may be invalid\n%s" % \
                (url, e))

    def http_put(self, path, fields):
        """
        Performs an HTTP PUT on the specified path, storing any cookies that
        were set.
        """
        url = self._make_url(path)
        debug('HTTP PUTting to %s: %s' % (url, fields))

        content_type, body = self._encode_multipart_formdata(fields, None)
        headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(body))
        }

        try:
            r = HTTPRequest(url, body, headers, method='PUT')
            data = urllib2.urlopen(r).read()
        except urllib2.HTTPError, e:
            # Re-raise so callers can interpret it.
            raise e

    def http_delete(self, path):
        """
        Performs an HTTP DELETE on the specified path, storing any cookies that
        were set.
        """
        url = self._make_url(path)
        debug('HTTP DELETing %s: %s' % (url, fields))

        try:
            r = HTTPRequest(url, body, headers, method='DELETE')
            data = urllib2.urlopen(r).read()
            self.cookie_jar.save(self.cookie_file)
            return data
            # Re-raise so callers can interpret it.
            raise e
        except urllib2.URLError, e:
            try:
                debug(e.read())
            except AttributeError:
                pass

            die("Unable to access %s. The host path may be invalid\n%s" % \
                (url, e))
        try:
            return self.process_json(self.http_post(path, fields, files))
        except urllib2.HTTPError, e:
            self.process_error(e.code, e.read())

    def api_put(self, path, fields=None):
        """
        Performs an API call using HTTP PUT at the specified path.
        """
        try:
            return self.process_json(self.http_put(path, fields))
        except urllib2.HTTPError, e:
            self.process_error(e.code, e.read())

    def api_delete(self, path):
        """
        Performs an API call using HTTP DELETE at the specified path.
        """
        try:
            return self.process_json(self.http_delete(path))
        except urllib2.HTTPError, e:
            self.process_error(e.code, e.read())
            content += str(fields[key]) + "\r\n"
    def check_options(self):
        pass

            # If repository_info is a list, check if any one entry is in trees.
            path = None

            if isinstance(repository_info.path, list):
                for path in repository_info.path:
                    if path in trees:
                        break
                else:
                    path = None
            elif repository_info.path in trees:
                path = repository_info.path

            if path and 'REVIEWBOARD_URL' in trees[path]:
                return trees[path]['REVIEWBOARD_URL']
        return self.do_diff(revs + args)
        return RepositoryInfo(path=options.repository_url,
                              base_path=options.repository_url,
                ["cleartool", "desc", "-pre", elem_path], split_lines=True)
                    if vkey.rfind("vobs") != -1 :
                        bpath = vkey[:vkey.rfind("vobs")+4]
                        fpath = vkey[vkey.rfind("vobs")+5:]
                    else :
                       bpath = vkey[:0]
                       fpath = vkey[1:]
        revs = revision_range.split(":")
        return self.do_diff(revs)[0]


                if cpath.isdir(filenam):
                    content = [
                        '%s\n' % s
                        for s in sorted(os.listdir(filenam))
                    ]
                    file_data.append(content)
                else:
                    fd = open(cpath.normpath(fn))
                    fdata = fd.readlines()
                    fd.close()
                    file_data.append(fdata)
                    # If the file was temp, it should be removed.
                    if do_rem:
                        os.remove(filenam)



        # Now that we know it's SVN, make sure we have GNU diff installed,
        # and error out if we don't.
        check_gnu_diff()

    def check_options(self):
        if (options.repository_url and
            not options.revision_range and
            not options.diff_filename):
            sys.stderr.write("The --repository-url option requires either the "
                             "--revision-range option or the --diff-filename "
                             "option.\n")
            sys.exit(1)

            files = []
            if len(args) == 1:
            elif len(args) > 1:
                files = args
            # When the source revision is zero, assume the user wants to
            # upload a diff containing all the files in ``base_path`` as new
            # files. If the base path within the repository is added to both
            # the old and new URLs, the ``svn diff`` command will error out
            # since the base_path didn't exist at revision zero. To avoid
            # that error, use the repository's root URL as the source for
            # the diff.
            if revisions[0] == "0":
                url = repository_info.path

            old_url = url + '@' + revisions[0]

                                 new_url] + files,
            # without much work. The info can also contain tabs after the
            # initial one; ignore those when splitting the string.
            parts = s.split("\t", 1)

            # If aliases exist for hostname, create a list of alias:port
            # strings for repository_path.
            if info[1]:
                servers = [info[0]] + info[1]
                repository_path = ["%s:%s" % (server, port)
                                   for server in servers]
            else:
                repository_path = "%s:%s" % (info[0], port)
        if len(args) == 0:
            return "default"
        elif len(args) == 1:
                # (if it isn't a number, it can't be a cln)
                return None
        # there are multiple args (not a cln)
        else:
            return None
                elif first_record['rev'] == second_record['rev']:
                    # We when we know the revisions are the same, we don't need
                    # to do any diffing. This speeds up large revision-range
                    # diffs quite a bit.
                    continue
            if v[0] < 2002 or (v[0] == "2002" and v[1] < 2):
            if re.search("no such changelist", description[0]):
                die("CLN %s does not exist." % changenum)

            # Some P4 wrappers are addding an extra line before the description
            if '*pending*' in description[0] or '*pending*' in description[1]:
        if cl_is_pending and (v[0] < 2002 or (v[0] == "2002" and v[1] < 2)
                              or changenum == "default"):
            # Pre-2002.2 doesn't give file list in pending changelists,
            # or we don't have a description for a default changeset,
            # so we have to get it a different way.
            if len(info) == 1 and info[0].startswith("File(s) not opened on this client."):
                die("Couldn't find any affected files for this change.")

            else:
                # Got to the end of all the description lines and didn't find
                # what we were looking for.
                die("Couldn't find any affected files for this change.")
            m = re.search(r'\.\.\. ([^#]+)#(\d+) '
                          r'(add|edit|delete|integrate|branch|move/add'
                          r'|move/delete)',
                          line)
            if changetype in ['edit', 'integrate']:
            elif changetype in ['add', 'branch', 'move/add']:
            elif changetype in ['delete', 'move/delete']:
           dl[0].startswith('Files %s and %s differ' %
                            (old_file, new_file)):
            dl = ['Binary files %s and %s differ\n' % (old_file, new_file)]
        elif len(dl) > 1:
            # Not everybody has files that end in a newline (ugh). This ensures
            # that the resulting diff file isn't broken.
            if dl[-1][-1] != '\n':
                dl.append('\n')
        else:
            die("ERROR, no valid diffs: %s" % dl[0])


    def __init__(self):
        self.hgrc = {}
        self._type = 'hg'
        self._hg_root = ''
        self._remote_path = ()
        self._hg_env = {
            'HGRCPATH': os.devnull,
            'HGPLAIN': '1',
        }

        # `self._remote_path_candidates` is an ordered set of hgrc
        # paths that are checked if `parent_branch` option is not given
        # explicitly.  The first candidate found to exist will be used,
        # falling back to `default` (the last member.)
        self._remote_path_candidates = ['reviewboard', 'origin', 'parent',
                                        'default']

        self._load_hgrc()

        if not self.hg_root:
        svn_info = execute(["hg", "svn", "info"], ignore_errors=True)
        if (not svn_info.startswith('abort:') and
            not svn_info.startswith("hg: unknown command") and
            not svn_info.lower().startswith('not a child of')):
            return self._calculate_hgsubversion_repository_info(svn_info)
        self._type = 'hg'
        path = self.hg_root
        base_path = '/'
        if self.hgrc:
            self._calculate_remote_path()
            if self._remote_path:
                path = self._remote_path[1]
                base_path = ''
        return RepositoryInfo(path=path, base_path=base_path,
                              supports_parent_diffs=True)
    def _calculate_remote_path(self):
        for candidate in self._remote_path_candidates:
            rc_key = 'paths.%s' % candidate
            if (not self._remote_path and self.hgrc.get(rc_key)):
                self._remote_path = (candidate, self.hgrc.get(rc_key))
                debug('Using candidate path %r: %r' % self._remote_path)
                return
    def _calculate_hgsubversion_repository_info(self, svn_info):
        self._type = 'svn'
        m = re.search(r'^Repository Root: (.+)$', svn_info, re.M)
        if not m:
            return None
        path = m.group(1)
        m2 = re.match(r'^(svn\+ssh|http|https|svn)://([-a-zA-Z0-9.]*@)(.*)$',
                        path)
        if m2:
            path = '%s://%s' % (m2.group(1), m2.group(3))
        m = re.search(r'^URL: (.+)$', svn_info, re.M)
        if not m:
            return None
        base_path = m.group(1)[len(path):] or "/"
        return RepositoryInfo(path=path, base_path=base_path,
    @property
    def hg_root(self):
        if not self._hg_root:
            root = execute(['hg', 'root'], env=self._hg_env,
                           ignore_errors=True)

            if not root.startswith('abort:'):
                self._hg_root = root.strip()
            else:
                self._hg_root = '.'

        return self._hg_root

    def _load_hgrc(self):
        for line in execute(['hg', 'showconfig'], split_lines=True):
            key, value = line.split('=', 1)
            self.hgrc[key] = value.strip()

    def extract_summary(self, revision):
        """
        Extracts the first line from the description of the given changeset.
        """
        return execute(['hg', 'log', '-r%s' % revision, '--template',
                        r'{desc|firstline}\n'], env=self._hg_env)

    def extract_description(self, rev1, rev2):
        """
        Extracts all descriptions in the given revision range and concatenates
        them, most recent ones going first.
        """
        numrevs = len(execute([
            'hg', 'log', '-r%s:%s' % (rev2, rev1),
            '--follow', '--template', r'{rev}\n'], env=self._hg_env
        ).strip().split('\n'))

        return execute(['hg', 'log', '-r%s:%s' % (rev2, rev1),
                        '--follow', '--template',
                        r'{desc}\n\n', '--limit',
                        str(numrevs - 1)], env=self._hg_env).strip()

        files = files or []
        if self._type == 'svn':
            return self._get_hgsubversion_diff(files)
        else:
            return self._get_outgoing_diff(files)
    def _get_hgsubversion_diff(self, files):
        parent = execute(['hg', 'parent', '--svn', '--template',
                          '{node}\n']).strip()
        if options.parent_branch:
            parent = options.parent_branch

        if options.guess_summary and not options.summary:
            options.summary = self.extract_summary(".")

        if options.guess_description and not options.description:
            options.description = self.extract_description(parent, ".")

        return (execute(["hg", "diff", "--svn", '-r%s:.' % parent]), None)

    def _get_outgoing_diff(self, files):
        """
        When working with a clone of a Mercurial remote, we need to find
        out what the outgoing revisions are for a given branch.  It would
        be nice if we could just do `hg outgoing --patch <remote>`, but
        there are a couple of problems with this.

        For one, the server-side diff parser isn't yet equipped to filter out
        diff headers such as "comparing with..." and "changeset: <rev>:<hash>".
        Another problem is that the output of `outgoing` potentially includes
        changesets across multiple branches.

        In order to provide the most accurate comparison between one's local
        clone and a given remote -- something akin to git's diff command syntax
        `git diff <treeish>..<treeish>` -- we have to do the following:

            - get the name of the current branch
            - get a list of outgoing changesets, specifying a custom format
            - filter outgoing changesets by the current branch name
            - get the "top" and "bottom" outgoing changesets
            - use these changesets as arguments to `hg diff -r <rev> -r <rev>`


        Future modifications may need to be made to account for odd cases like
        having multiple diverged branches which share partial history -- or we
        can just punish developers for doing such nonsense :)
        """
        files = files or []

        remote = self._remote_path[0]

        if not remote and options.parent_branch:
            remote = options.parent_branch
        current_branch = execute(['hg', 'branch'], env=self._hg_env).strip()
        outgoing_changesets = \
            self._get_outgoing_changesets(current_branch, remote)

        top_rev, bottom_rev = \
            self._get_top_and_bottom_outgoing_revs(outgoing_changesets)

        full_command = ['hg', 'diff', '-r', str(bottom_rev), '-r',
                        str(top_rev)] + files

        return (execute(full_command, env=self._hg_env), None)

    def _get_outgoing_changesets(self, current_branch, remote):
        """
        Given the current branch name and a remote path, return a list
        of outgoing changeset numbers.
        """
        outgoing_changesets = []
        raw_outgoing = execute(['hg', '-q', 'outgoing', '--template',
                                'b:{branches}\nr:{rev}\n\n', remote],
                               env=self._hg_env)

        for pair in raw_outgoing.split('\n\n'):
            if not pair.strip():
                continue

            branch, rev = pair.strip().split('\n')

            branch_name = branch[len('b:'):].strip()
            branch_name = branch_name or 'default'
            revno = rev[len('r:'):]

            if branch_name == current_branch and revno.isdigit():
                debug('Found outgoing changeset %s for branch %r'
                      % (revno, branch_name))
                outgoing_changesets.append(int(revno))

        return outgoing_changesets

    def _get_top_and_bottom_outgoing_revs(cls, outgoing_changesets):
        # This is a classmethod rather than a func mostly just to keep the
        # module namespace clean.  Pylint told me to do it.
        top_rev = max(outgoing_changesets)
        bottom_rev = min(outgoing_changesets)
        bottom_rev = max([0, bottom_rev - 1])

        return top_rev, bottom_rev

    # postfix decorators to stay pre-2.5 compatible
    _get_top_and_bottom_outgoing_revs = \
        classmethod(_get_top_and_bottom_outgoing_revs)
        if self._type != 'hg':

        if options.guess_summary and not options.summary:
            options.summary = self.extract_summary(r2)

        if options.guess_description and not options.description:
            options.description = self.extract_description(r1, r2)

        return execute(["hg", "diff", "-r", r1, "-r", r2],
                       env=self._hg_env)

    def scan_for_server(self, repository_info):
        # Scan first for dot files, since it's faster and will cover the
        # user's $HOME/.reviewboardrc
        server_url = \
            super(MercurialClient, self).scan_for_server(repository_info)

        if not server_url and self.hgrc.get('reviewboard.url'):
            server_url = self.hgrc.get('reviewboard.url').strip()

        if not server_url and self._type == "svn":
            # Try using the reviewboard:url property on the SVN repo, if it
            # exists.
            prop = SVNClient().scan_for_server_property(repository_info)

            if prop:
                return prop

        return server_url
    def _strip_heads_prefix(self, ref):
        """ Strips prefix from ref name, if possible """
        return re.sub(r'^refs/heads/', '', ref)

        self.head_ref = execute(['git', 'symbolic-ref', '-q', 'HEAD']).strip()

                    self.upstream_branch = options.parent_branch or 'master'
        # Check for a tracking branch and determine merge-base
        short_head = self._strip_heads_prefix(self.head_ref)
        merge = execute(['git', 'config', '--get',
                         'branch.%s.merge' % short_head],
                        ignore_errors=True).strip()
        remote = execute(['git', 'config', '--get',
                          'branch.%s.remote' % short_head],
                         ignore_errors=True).strip()

        merge = self._strip_heads_prefix(merge)
        self.upstream_branch = ''

        if remote and remote != '.' and merge:
            self.upstream_branch = '%s/%s' % (remote, merge)

        self.upstream_branch, origin_url = self.get_origin(self.upstream_branch,
                                                       True)

        if not origin_url or origin_url.startswith("fatal:"):
            self.upstream_branch, origin_url = self.get_origin()

        url = origin_url.rstrip('/')
        if url:
            self.type = "git"
            return RepositoryInfo(path=url, base_path='',
                                  supports_parent_diffs=True)
    def get_origin(self, default_upstream_branch=None, ignore_errors=False):
        """Get upstream remote origin from options or parameters.

        Returns a tuple: (upstream_branch, remote_url)
        """
        upstream_branch = options.tracking or default_upstream_branch or \
                          'origin/master'
        upstream_remote = upstream_branch.split('/')[0]
        origin_url = execute(["git", "config", "remote.%s.url" % upstream_remote],
                         ignore_errors=ignore_errors)

        return (upstream_branch, origin_url.rstrip('\n'))

        parent_branch = options.parent_branch
        self.merge_base = execute(["git", "merge-base", self.upstream_branch,
                                   self.head_ref]).strip()
        if parent_branch:
            diff_lines = self.make_diff(parent_branch)
            parent_diff_lines = self.make_diff(self.merge_base, parent_branch)
            diff_lines = self.make_diff(self.merge_base, self.head_ref)
                ["git", "log", "--pretty=format:%s%n%n%b",
                 (parent_branch or self.merge_base) + ".."],
    def make_diff(self, ancestor, commit=""):
        rev_range = "%s..%s" % (ancestor, commit)

                                  "--no-ext-diff", "-r", "-u", rev_range],
            return self.make_svn_diff(ancestor, diff_lines)
                            "--no-ext-diff", rev_range])
        rev = execute(["git", "svn", "find-rev", parent_branch]).strip()
            elif line.startswith("new file mode"):
                # Filter this out.
                pass
            elif line.startswith("Binary files "):
                # Add the following so that we know binary files were added/changed
                diff_data += "Cannot display: file marked as a binary type.\n"
                diff_data += "svn:mime-type = application/octet-stream\n"
        """Perform a diff between two arbitrary revisions"""
        if ":" not in revision_range:
            # only one revision is specified
            if options.guess_summary and not options.summary:
                options.summary = execute(
                    ["git", "log", "--pretty=format:%s", revision_range + ".."],
                    ignore_errors=True).strip()

            if options.guess_description and not options.description:
                options.description = execute(
                    ["git", "log", "--pretty=format:%s%n%n%b", revision_range + ".."],
                    ignore_errors=True).strip()

            return self.make_diff(revision_range)
        else:
            r1, r2 = revision_range.split(":")

            if options.guess_summary and not options.summary:
                options.summary = execute(
                    ["git", "log", "--pretty=format:%s", "%s..%s" % (r1, r2)],
                    ignore_errors=True).strip()

            if options.guess_description and not options.description:
                options.description = execute(
                    ["git", "log", "--pretty=format:%s%n%n%b", "%s..%s" % (r1, r2)],
                    ignore_errors=True).strip()

            return self.make_diff(r1, r2)
def check_gnu_diff():
    """Checks if GNU diff is installed, and informs the user if it's not."""
    has_gnu_diff = False

    try:
        result = execute(['diff', '--version'], ignore_errors=True)
        has_gnu_diff = 'GNU diffutils' in result
    except OSError:
        pass

    if not has_gnu_diff:
        sys.stderr.write('\n')
        sys.stderr.write('GNU diff is required for Subversion '
                         'repositories. Make sure it is installed\n')
        sys.stderr.write('and in the path.\n')
        sys.stderr.write('\n')

        if os.name == 'nt':
            sys.stderr.write('On Windows, you can install this from:\n')
            sys.stderr.write(GNU_DIFF_WIN32_URL)
            sys.stderr.write('\n')

        die()


        except SyntaxError, e:
            die('Syntax error in config file: %s\n'
                'Line %i offset %i\n' % (filename, e.lineno, e.offset))
        if options.bugs_closed:     # append to existing list
            options.bugs_closed = options.bugs_closed.strip(", ")
            bug_set = set(re.split("[, ]+", options.bugs_closed)) | \
                      set(review_request['bugs_closed'])
            options.bugs_closed = ",".join(bug_set)
        if e.error_code == 103: # Not logged in
            die("Error getting review request %s: %s" % (options.rid, e))
            die("Error creating review request: %s" % e)
            sys.stderr.write('\n')
            sys.stderr.write('Error uploading diff\n')
            sys.stderr.write('\n')

            if e.error_code == 105:
                sys.stderr.write('The generated diff file was empty. This '
                                 'usually means no files were\n')
                sys.stderr.write('modified in this change.\n')
                sys.stderr.write('\n')
                sys.stderr.write('Try running with --output-diff and --debug '
                                 'for more information.\n')
                sys.stderr.write('\n')

    if options.reopen:
        server.reopen(review_request)

    request_url = 'r/' + str(review_request['id']) + '/'
                          version="RBTools " + get_version_string())
    parser.add_option("--reopen",
                      dest="reopen", action="store_true", default=False,
                      help="reopen discarded review request "
                           "after update")
                           "hg/hgsubversion only)")
                           "(git/hg/hgsubversion only)")
    parser.add_option("--tracking-branch",
                      dest="tracking", default=None,
                      metavar="TRACKING",
                      help="Tracking branch from which your branch is derived "
                           "(git only, defaults to origin/master)")
                           "outside of a working copy (currently only "
                           "supported by Subversion with --revision-range or "
                           "--diff-filename and ClearCase with relative "
                           "paths outside the view)")
    parser.add_option("--diff-filename",
                      dest="diff_filename", default=None,
                      help='upload an existing diff file, instead of '
                           'generating a new diff')
    if options.reopen and not options.rid:
        sys.stderr.write("The --reopen option requires "
                         "--review-request-id option.\n")
def determine_client():

    origcwd = os.path.abspath(os.getcwd())

    # Verify that options specific to an SCM Client have not been mis-used.
    tool.check_options()

    elif options.diff_filename:
        parent_diff = None

        if options.diff_filename == '-':
            diff = sys.stdin.read()
        else:
            try:
                fp = open(os.path.join(origcwd, options.diff_filename), 'r')
                diff = fp.read()
                fp.close()
            except IOError, e:
                die("Unable to open diff filename: %s" % e)
    if len(diff) == 0:
        die("There don't seem to be any diffs!")

        # The comma here isn't a typo, but rather suppresses the extra newline
        print diff,