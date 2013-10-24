from rbtools.clients.perforce import PerforceClient
                        if getattr(self.options, 'parent_branch', None):
                svn_remote = execute(
                    [self.git, "config", "--get", "svn-remote.svn.url"],
                    ignore_errors=True)
                if (version_parts and svn_remote and
                                              (1, 5, 4))):
        # Okay, maybe Perforce (git-p4).
        git_p4_ref = os.path.join(git_dir, 'refs', 'remotes', 'p4', 'master')
        data = execute([self.git, 'config', '--get', 'git-p4.port'],
                       ignore_errors=True)
        m = re.search(r'(.+)', data)
        if m and os.path.exists(git_p4_ref):
            port = m.group(1)
            self.type = 'perforce'
            self.upstream_branch = 'remotes/p4/master'
            return RepositoryInfo(path=port,
                                  base_path='',
                                  supports_parent_diffs=True)
            self.upstream_branch = self.get_origin(self.upstream_branch,
                                                   True)[0]
        origin_url = execute(
            [self.git, "config", "--get", "remote.%s.url" % upstream_remote],
            ignore_errors=True).rstrip("\n")
            if prop:
                return prop
        elif self.type == 'perforce':
            prop = PerforceClient().scan_for_server(repository_info)

        if self.type == 'perforce':
            parent_branch = self.options.parent_branch or 'p4'
        else:
            parent_branch = self.options.parent_branch

            self.options.summary = execute(
                [self.git, "log", "--pretty=format:%s", "HEAD^!"],
                ignore_errors=True).strip()
        return {
            'diff': diff_lines,
            'parent_diff': parent_diff_lines,
            'base_commit_id': self.merge_base,
        }
        elif self.type == "perforce":
            diff_lines = execute([self.git, "diff", "--no-color",
                                  "--no-prefix", "-r", "-u", rev_range],
                                 split_lines=True)
            return self.make_perforce_diff(ancestor, diff_lines)
        if not rev and self.merge_base:
            rev = execute([self.git, "svn", "find-rev",
                           self.merge_base]).strip()

    def make_perforce_diff(self, parent_branch, diff_lines):
        """Format the output of git diff to look more like perforce's."""
        diff_data = ''
        filename = ''
        p4rev = ''

        # Find which depot changelist we're based on
        log = execute([self.git, 'log', parent_branch], ignore_errors=True)

        for line in log:
            m = re.search(r'repo-paths = "(.+)": change = (\d+)\]', log, re.M)
            if m:
                base_path = m.group(1).strip()
                p4rev = m.group(2).strip()
                break

        for line in diff_lines:
            if line.startswith('diff '):
                # Grab the filename and then filter this out.
                # This will be in the format of:
                #    diff --git a/path/to/file b/path/to/file
                filename = line.split(' ')[2].strip()
            elif (line.startswith('index ') or
                  line.startswith('new file mode ')):
                # Filter this out
                pass
            elif line.startswith('--- '):
                data = execute(
                    ['p4', 'files', base_path + filename + '@' + p4rev],
                    ignore_errors=True)
                m = re.search(r'^%s%s#(\d+).*$' % (re.escape(base_path),
                                                   re.escape(filename)),
                              data, re.M)
                if m:
                    fileVersion = m.group(1).strip()
                else:
                    fileVersion = 1

                diff_data += '--- %s%s\t%s%s#%s\n' % (base_path, filename,
                                                      base_path, filename,
                                                      fileVersion)
            elif line.startswith('+++ '):
                # TODO: add a real timestamp
                diff_data += '+++ %s%s\t%s\n' % (base_path, filename,
                                                 'TIMESTAMP')
            else:
                diff_data += line

        return diff_data

                self.options.summary = execute(
                    [self.git, "log", "--pretty=format:%s", "HEAD^!"],
                    ignore_errors=True).strip()
            diff_lines = self.make_diff(revision_range)
                self.options.summary = execute(
                    [self.git, "log", "--pretty=format:%s", "%s^!" % r2],
                    ignore_errors=True).strip()
            diff_lines = self.make_diff(r1, r2)

        return {
            'diff': diff_lines,
            'parent_diff_lines': parent_diff_lines,
            'base_commit_id': self.merge_base,
        }