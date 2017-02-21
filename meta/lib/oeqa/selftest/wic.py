#!/usr/bin/env python
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# Copyright (c) 2015, Intel Corporation.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# AUTHORS
# Ed Bartosh <ed.bartosh@linux.intel.com>

"""Test cases for wic."""

import os

from glob import glob
from shutil import rmtree

from oeqa.selftest.base import oeSelfTest
from oeqa.utils.commands import runCmd, bitbake, get_bb_var, get_bb_vars, runqemu
from oeqa.utils.decorators import testcase


class Wic(oeSelfTest):
    """Wic test class."""

    resultdir = "/var/tmp/wic.oe-selftest/"
    image_is_ready = False
    wicenv_cache = {}

    def setUpLocal(self):
        """This code is executed before each test method."""
        self.write_config('MACHINE_FEATURES_append = " efi"\n')

        # Do this here instead of in setUpClass as the base setUp does some
        # clean up which can result in the native tools built earlier in
        # setUpClass being unavailable.
        if not Wic.image_is_ready:
            bitbake('wic-tools')
            bitbake('core-image-minimal')
            Wic.image_is_ready = True

        rmtree(self.resultdir, ignore_errors=True)

    def tearDownLocal(self):
        """Remove resultdir as it may contain images."""
        rmtree(self.resultdir, ignore_errors=True)

    @testcase(1552)
    def test_version(self):
        """Test wic --version"""
        self.assertEqual(0, runCmd('wic --version').status)

    @testcase(1208)
    def test_help(self):
        """Test wic --help and wic -h"""
        self.assertEqual(0, runCmd('wic --help').status)
        self.assertEqual(0, runCmd('wic -h').status)

    @testcase(1209)
    def test_createhelp(self):
        """Test wic create --help"""
        self.assertEqual(0, runCmd('wic create --help').status)

    @testcase(1210)
    def test_listhelp(self):
        """Test wic list --help"""
        self.assertEqual(0, runCmd('wic list --help').status)

    @testcase(1553)
    def test_help_create(self):
        """Test wic help create"""
        self.assertEqual(0, runCmd('wic help create').status)

    @testcase(1554)
    def test_help_list(self):
        """Test wic help list"""
        self.assertEqual(0, runCmd('wic help list').status)

    @testcase(1215)
    def test_help_overview(self):
        """Test wic help overview"""
        self.assertEqual(0, runCmd('wic help overview').status)

    @testcase(1216)
    def test_help_plugins(self):
        """Test wic help plugins"""
        self.assertEqual(0, runCmd('wic help plugins').status)

    @testcase(1217)
    def test_help_kickstart(self):
        """Test wic help kickstart"""
        self.assertEqual(0, runCmd('wic help kickstart').status)

    @testcase(1555)
    def test_list_images(self):
        """Test wic list images"""
        self.assertEqual(0, runCmd('wic list images').status)

    @testcase(1556)
    def test_list_source_plugins(self):
        """Test wic list source-plugins"""
        self.assertEqual(0, runCmd('wic list source-plugins').status)

    @testcase(1557)
    def test_listed_images_help(self):
        """Test wic listed images help"""
        output = runCmd('wic list images').output
        imagelist = [line.split()[0] for line in output.splitlines()]
        for image in imagelist:
            self.assertEqual(0, runCmd('wic list %s help' % image).status)

    @testcase(1213)
    def test_unsupported_subcommand(self):
        """Test unsupported subcommand"""
        self.assertEqual(1, runCmd('wic unsupported',
                                   ignore_status=True).status)

    @testcase(1214)
    def test_no_command(self):
        """Test wic without command"""
        self.assertEqual(1, runCmd('wic', ignore_status=True).status)

    @testcase(1211)
    def test_build_image_name(self):
        """Test wic create directdisk --image-name=core-image-minimal"""
        cmd = "wic create directdisk --image-name=core-image-minimal -o %s" % self.resultdir
        self.assertEqual(0, runCmd(cmd).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct")))

    @testcase(1157)
    def test_gpt_image(self):
        """Test creation of core-image-minimal with gpt table and UUID boot"""
        cmd = "wic create directdisk-gpt --image-name core-image-minimal -o %s" % self.resultdir
        self.assertEqual(0, runCmd(cmd).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct")))

    @testcase(1346)
    def test_iso_image(self):
        """Test creation of hybrid iso image with legacy and EFI boot"""
        config = 'INITRAMFS_IMAGE = "core-image-minimal-initramfs"\n'\
                 'MACHINE_FEATURES_append = " efi"\n'
        self.append_config(config)
        bitbake('core-image-minimal')
        self.remove_config(config)
        cmd = "wic create mkhybridiso --image-name core-image-minimal -o %s" % self.resultdir
        self.assertEqual(0, runCmd(cmd).status)
        self.assertEqual(1, len(glob(self.resultdir + "HYBRID_ISO_IMG-*.direct")))
        self.assertEqual(1, len(glob(self.resultdir + "HYBRID_ISO_IMG-*.iso")))

    @testcase(1348)
    def test_qemux86_directdisk(self):
        """Test creation of qemux-86-directdisk image"""
        cmd = "wic create qemux86-directdisk -e core-image-minimal -o %s" % self.resultdir
        self.assertEqual(0, runCmd(cmd).status)
        self.assertEqual(1, len(glob(self.resultdir + "qemux86-directdisk-*direct")))

    @testcase(1350)
    def test_mkefidisk(self):
        """Test creation of mkefidisk image"""
        cmd = "wic create mkefidisk -e core-image-minimal -o %s" % self.resultdir
        self.assertEqual(0, runCmd(cmd).status)
        self.assertEqual(1, len(glob(self.resultdir + "mkefidisk-*direct")))

    @testcase(1385)
    def test_directdisk_bootloader_config(self):
        """Test creation of directdisk-bootloader-config image"""
        cmd = "wic create directdisk-bootloader-config -e core-image-minimal -o %s" % self.resultdir
        self.assertEqual(0, runCmd(cmd).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-bootloader-config-*direct")))

    @testcase(1560)
    def test_systemd_bootdisk(self):
        """Test creation of systemd-bootdisk image"""
        config = 'MACHINE_FEATURES_append = " efi"\n'
        self.append_config(config)
        bitbake('core-image-minimal')
        self.remove_config(config)
        cmd = "wic create systemd-bootdisk -e core-image-minimal -o %s" % self.resultdir
        self.assertEqual(0, runCmd(cmd).status)
        self.assertEqual(1, len(glob(self.resultdir + "systemd-bootdisk-*direct")))

    @testcase(1561)
    def test_sdimage_bootpart(self):
        """Test creation of sdimage-bootpart image"""
        cmd = "wic create sdimage-bootpart -e core-image-minimal -o %s" % self.resultdir
        self.write_config('IMAGE_BOOT_FILES = "bzImage"\n')
        self.assertEqual(0, runCmd(cmd).status)
        self.assertEqual(1, len(glob(self.resultdir + "sdimage-bootpart-*direct")))

    @testcase(1562)
    def test_default_output_dir(self):
        """Test default output location"""
        for fname in glob("directdisk-*.direct"):
            os.remove(fname)
        cmd = "wic create directdisk -e core-image-minimal"
        self.assertEqual(0, runCmd(cmd).status)
        self.assertEqual(1, len(glob("directdisk-*.direct")))

    @testcase(1212)
    def test_build_artifacts(self):
        """Test wic create directdisk providing all artifacts."""
        bb_vars = get_bb_vars(['STAGING_DATADIR', 'RECIPE_SYSROOT_NATIVE'],
                               'wic-tools')
        bb_vars.update(get_bb_vars(['DEPLOY_DIR_IMAGE', 'IMAGE_ROOTFS'],
                                 'core-image-minimal'))
        bbvars = {key.lower(): value for key, value in bb_vars.items()}
        bbvars['resultdir'] = self.resultdir
        status = runCmd("wic create directdisk "
                        "-b %(staging_datadir)s "
                        "-k %(deploy_dir_image)s "
                        "-n %(recipe_sysroot_native)s "
                        "-r %(image_rootfs)s "
                        "-o %(resultdir)s" % bbvars).status
        self.assertEqual(0, status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct")))

    @testcase(1264)
    def test_compress_gzip(self):
        """Test compressing an image with gzip"""
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name core-image-minimal "
                                   "-c gzip -o %s" % self.resultdir).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct.gz")))

    @testcase(1265)
    def test_compress_bzip2(self):
        """Test compressing an image with bzip2"""
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=core-image-minimal "
                                   "-c bzip2 -o %s" % self.resultdir).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct.bz2")))

    @testcase(1266)
    def test_compress_xz(self):
        """Test compressing an image with xz"""
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=core-image-minimal "
                                   "--compress-with=xz -o %s" % self.resultdir).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct.xz")))

    @testcase(1267)
    def test_wrong_compressor(self):
        """Test how wic breaks if wrong compressor is provided"""
        self.assertEqual(2, runCmd("wic create directdisk "
                                   "--image-name=core-image-minimal "
                                   "-c wrong -o %s" % self.resultdir,
                                   ignore_status=True).status)

    @testcase(1558)
    def test_debug_short(self):
        """Test -D option"""
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=core-image-minimal "
                                   "-D -o %s" % self.resultdir).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct")))

    def test_debug_long(self):
        """Test --debug option"""
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=core-image-minimal "
                                   "--debug -o %s" % self.resultdir).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct")))

    @testcase(1563)
    def test_skip_build_check_short(self):
        """Test -s option"""
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=core-image-minimal "
                                   "-s -o %s" % self.resultdir).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct")))

    def test_skip_build_check_long(self):
        """Test --skip-build-check option"""
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=core-image-minimal "
                                   "--skip-build-check "
                                   "--outdir %s" % self.resultdir).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct")))

    @testcase(1564)
    def test_build_rootfs_short(self):
        """Test -f option"""
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=core-image-minimal "
                                   "-f -o %s" % self.resultdir).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct")))

    def test_build_rootfs_long(self):
        """Test --build-rootfs option"""
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=core-image-minimal "
                                   "--build-rootfs "
                                   "--outdir %s" % self.resultdir).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*.direct")))

    @testcase(1268)
    def test_rootfs_indirect_recipes(self):
        """Test usage of rootfs plugin with rootfs recipes"""
        status = runCmd("wic create directdisk-multi-rootfs "
                        "--image-name=core-image-minimal "
                        "--rootfs rootfs1=core-image-minimal "
                        "--rootfs rootfs2=core-image-minimal "
                        "--outdir %s" % self.resultdir).status
        self.assertEqual(0, status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-multi-rootfs*.direct")))

    @testcase(1269)
    def test_rootfs_artifacts(self):
        """Test usage of rootfs plugin with rootfs paths"""
        bb_vars = get_bb_vars(['STAGING_DATADIR', 'RECIPE_SYSROOT_NATIVE'],
                               'wic-tools')
        bb_vars.update(get_bb_vars(['DEPLOY_DIR_IMAGE', 'IMAGE_ROOTFS'],
                                 'core-image-minimal'))
        bbvars = {key.lower(): value for key, value in bb_vars.items()}
        bbvars['wks'] = "directdisk-multi-rootfs"
        bbvars['resultdir'] = self.resultdir
        status = runCmd("wic create %(wks)s "
                        "--bootimg-dir=%(staging_datadir)s "
                        "--kernel-dir=%(deploy_dir_image)s "
                        "--native-sysroot=%(recipe_sysroot_native)s "
                        "--rootfs-dir rootfs1=%(image_rootfs)s "
                        "--rootfs-dir rootfs2=%(image_rootfs)s "
                        "--outdir %(resultdir)s" % bbvars).status
        self.assertEqual(0, status)
        self.assertEqual(1, len(glob(self.resultdir + "%(wks)s-*.direct" % bbvars)))

    def test_exclude_path(self):
        """Test --exclude-path wks option."""

        oldpath = os.environ['PATH']
        os.environ['PATH'] = get_bb_var("PATH", "wic-tools")

        try:
            wks_file = 'temp.wks'
            with open(wks_file, 'w') as wks:
                rootfs_dir = get_bb_var('IMAGE_ROOTFS', 'core-image-minimal')
                wks.write("""part / --source rootfs --ondisk mmcblk0 --fstype=ext4 --exclude-path usr
part /usr --source rootfs --ondisk mmcblk0 --fstype=ext4 --rootfs-dir %s/usr
part /etc --source rootfs --ondisk mmcblk0 --fstype=ext4 --exclude-path bin/ --rootfs-dir %s/usr"""
                          % (rootfs_dir, rootfs_dir))
            self.assertEqual(0, runCmd("wic create %s -e core-image-minimal -o %s" \
                                       % (wks_file, self.resultdir)).status)

            os.remove(wks_file)
            wicout = glob(self.resultdir + "%s-*direct" % 'temp')
            self.assertEqual(1, len(wicout))

            wicimg = wicout[0]

            # verify partition size with wic
            res = runCmd("parted -m %s unit b p 2>/dev/null" % wicimg)
            self.assertEqual(0, res.status)

            # parse parted output which looks like this:
            # BYT;\n
            # /var/tmp/wic/build/tmpfwvjjkf_-201611101222-hda.direct:200MiB:file:512:512:msdos::;\n
            # 1:0.00MiB:200MiB:200MiB:ext4::;\n
            partlns = res.output.splitlines()[2:]

            self.assertEqual(3, len(partlns))

            for part in [1, 2, 3]:
                part_file = os.path.join(self.resultdir, "selftest_img.part%d" % part)
                partln = partlns[part-1].split(":")
                self.assertEqual(7, len(partln))
                start = int(partln[1].rstrip("B")) / 512
                length = int(partln[3].rstrip("B")) / 512
                self.assertEqual(0, runCmd("dd if=%s of=%s skip=%d count=%d" %
                                           (wicimg, part_file, start, length)).status)

            # Test partition 1, should contain the normal root directories, except
            # /usr.
            res = runCmd("debugfs -R 'ls -p' %s 2>/dev/null" % os.path.join(self.resultdir, "selftest_img.part1"))
            self.assertEqual(0, res.status)
            files = [line.split('/')[5] for line in res.output.split('\n')]
            self.assertIn("etc", files)
            self.assertNotIn("usr", files)

            # Partition 2, should contain common directories for /usr, not root
            # directories.
            res = runCmd("debugfs -R 'ls -p' %s 2>/dev/null" % os.path.join(self.resultdir, "selftest_img.part2"))
            self.assertEqual(0, res.status)
            files = [line.split('/')[5] for line in res.output.split('\n')]
            self.assertNotIn("etc", files)
            self.assertNotIn("usr", files)
            self.assertIn("share", files)

            # Partition 3, should contain the same as partition 2, including the bin
            # directory, but not the files inside it.
            res = runCmd("debugfs -R 'ls -p' %s 2>/dev/null" % os.path.join(self.resultdir, "selftest_img.part3"))
            self.assertEqual(0, res.status)
            files = [line.split('/')[5] for line in res.output.split('\n')]
            self.assertNotIn("etc", files)
            self.assertNotIn("usr", files)
            self.assertIn("share", files)
            self.assertIn("bin", files)
            res = runCmd("debugfs -R 'ls -p bin' %s 2>/dev/null" % os.path.join(self.resultdir, "selftest_img.part3"))
            self.assertEqual(0, res.status)
            files = [line.split('/')[5] for line in res.output.split('\n')]
            self.assertIn(".", files)
            self.assertIn("..", files)
            self.assertEqual(2, len(files))

            for part in [1, 2, 3]:
                part_file = os.path.join(self.resultdir, "selftest_img.part%d" % part)
                os.remove(part_file)

        finally:
            os.environ['PATH'] = oldpath

    def test_exclude_path_errors(self):
        """Test --exclude-path wks option error handling."""
        wks_file = 'temp.wks'

        rootfs_dir = get_bb_var('IMAGE_ROOTFS', 'core-image-minimal')

        # Absolute argument.
        with open(wks_file, 'w') as wks:
            wks.write("part / --source rootfs --ondisk mmcblk0 --fstype=ext4 --exclude-path /usr")
        self.assertNotEqual(0, runCmd("wic create %s -e core-image-minimal -o %s" \
                                      % (wks_file, self.resultdir), ignore_status=True).status)
        os.remove(wks_file)

        # Argument pointing to parent directory.
        with open(wks_file, 'w') as wks:
            wks.write("part / --source rootfs --ondisk mmcblk0 --fstype=ext4 --exclude-path ././..")
        self.assertNotEqual(0, runCmd("wic create %s -e core-image-minimal -o %s" \
                                      % (wks_file, self.resultdir), ignore_status=True).status)
        os.remove(wks_file)

    @testcase(1496)
    def test_bmap_short(self):
        """Test generation of .bmap file -m option"""
        cmd = "wic create directdisk -e core-image-minimal -m -o %s" % self.resultdir
        status = runCmd(cmd).status
        self.assertEqual(0, status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*direct")))
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*direct.bmap")))

    def test_bmap_long(self):
        """Test generation of .bmap file --bmap option"""
        cmd = "wic create directdisk -e core-image-minimal --bmap -o %s" % self.resultdir
        status = runCmd(cmd).status
        self.assertEqual(0, status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*direct")))
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*direct.bmap")))

    def _get_image_env_path(self, image):
        """Generate and obtain the path to <image>.env"""
        if image not in self.wicenv_cache:
            self.assertEqual(0, bitbake('%s -c do_rootfs_wicenv' % image).status)
            bb_vars = get_bb_vars(['STAGING_DIR', 'MACHINE'], image)
            stdir = bb_vars['STAGING_DIR']
            machine = bb_vars['MACHINE']
            self.wicenv_cache[image] = os.path.join(stdir, machine, 'imgdata')
        return self.wicenv_cache[image]

    @testcase(1347)
    def test_image_env(self):
        """Test generation of <image>.env files."""
        image = 'core-image-minimal'
        imgdatadir = self._get_image_env_path(image)

        bb_vars = get_bb_vars(['IMAGE_BASENAME', 'WICVARS'], image)
        basename = bb_vars['IMAGE_BASENAME']
        self.assertEqual(basename, image)
        path = os.path.join(imgdatadir, basename) + '.env'
        self.assertTrue(os.path.isfile(path))

        wicvars = set(bb_vars['WICVARS'].split())
        # filter out optional variables
        wicvars = wicvars.difference(('DEPLOY_DIR_IMAGE', 'IMAGE_BOOT_FILES',
                                      'INITRD', 'INITRD_LIVE', 'ISODIR'))
        with open(path) as envfile:
            content = dict(line.split("=", 1) for line in envfile)
            # test if variables used by wic present in the .env file
            for var in wicvars:
                self.assertTrue(var in content, "%s is not in .env file" % var)
                self.assertTrue(content[var])

    @testcase(1559)
    def test_image_vars_dir_short(self):
        """Test image vars directory selection -v option"""
        image = 'core-image-minimal'
        imgenvdir = self._get_image_env_path(image)

        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=%s -v %s -o %s"
                                   % (image, imgenvdir, self.resultdir)).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*direct")))

    def test_image_vars_dir_long(self):
        """Test image vars directory selection --vars option"""
        image = 'core-image-minimal'
        imgenvdir = self._get_image_env_path(image)
        self.assertEqual(0, runCmd("wic create directdisk "
                                   "--image-name=%s "
                                   "--vars %s "
                                   "--outdir %s"
                                   % (image, imgenvdir, self.resultdir)).status)
        self.assertEqual(1, len(glob(self.resultdir + "directdisk-*direct")))

    @testcase(1351)
    def test_wic_image_type(self):
        """Test building wic images by bitbake"""
        config = 'IMAGE_FSTYPES += "wic"\nWKS_FILE = "wic-image-minimal"\n'\
                 'MACHINE_FEATURES_append = " efi"\n'
        self.append_config(config)
        self.assertEqual(0, bitbake('wic-image-minimal').status)
        self.remove_config(config)

        bb_vars = get_bb_vars(['DEPLOY_DIR_IMAGE', 'MACHINE'])
        deploy_dir = bb_vars['DEPLOY_DIR_IMAGE']
        machine = bb_vars['MACHINE']
        prefix = os.path.join(deploy_dir, 'wic-image-minimal-%s.' % machine)
        # check if we have result image and manifests symlinks
        # pointing to existing files
        for suffix in ('wic', 'manifest'):
            path = prefix + suffix
            self.assertTrue(os.path.islink(path))
            self.assertTrue(os.path.isfile(os.path.realpath(path)))

    @testcase(1422)
    def test_qemu(self):
        """Test wic-image-minimal under qemu"""
        config = 'IMAGE_FSTYPES += "wic"\nWKS_FILE = "wic-image-minimal"\n'\
                 'MACHINE_FEATURES_append = " efi"\n'
        self.append_config(config)
        self.assertEqual(0, bitbake('wic-image-minimal').status)
        self.remove_config(config)

        with runqemu('wic-image-minimal', ssh=False) as qemu:
            cmd = "mount |grep '^/dev/' | cut -f1,3 -d ' '"
            status, output = qemu.run_serial(cmd)
            self.assertEqual(1, status, 'Failed to run command "%s": %s' % (cmd, output))
            self.assertEqual(output, '/dev/root /\r\n/dev/vda3 /mnt')
