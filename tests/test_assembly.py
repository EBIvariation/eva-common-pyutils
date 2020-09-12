import os
import shutil
from unittest.mock import Mock

from ebi_eva_common_pyutils.assembly.assembly import NCBIAssembly
from tests.test_common import TestCommon


class TestNCBIAssembly(TestCommon):

    assembly_report = os.path.join(os.path.dirname(os.path.dirname(__file__)), "GCA_000000000.0_assembly_report.txt")
    assembly_report_header = (
        '# Sequence-Name', 'Sequence-Role', 'Assigned-Molecule', 'Assigned-Molecule-Location/Type','GenBank-Accn',
        'Relationship', 'RefSeq-Accn', 'Assembly-Unit', 'Sequence-Length', 'UCSC-style-name'
    )
    assembly_report_line1 = (
        'scaffold_3134', 'unplaced-scaffold', 'na', 'na', 'LODP01002389.1', '=', 'NW_017892567.1', 'Primary Assembly',
        '3525', 'na'
    )

    def setUp(self) -> None:
        self.genome_folder = os.path.join(self.resources_folder, 'genomes')
        os.makedirs(self.genome_folder, exist_ok=True)
        self.assembly = NCBIAssembly('GCA_000008865.1', 'Escherichia coli O157:H7 str. Sakai', self.genome_folder)

        # Fake assembly that will be downloaded from pre-made report
        self.assembly_from_report = NCBIAssembly('GCA_000000000.0', 'Thingy thung', self.genome_folder)
        assembly_dir = os.path.join(self.genome_folder, 'thingy_thung', 'GCA_000000000.0')
        os.makedirs(assembly_dir, exist_ok=True)
        with open(os.path.join(assembly_dir, 'GCA_000000000.0_assembly_report.txt'), 'w') as open_file:
            lines = ['\t'.join(l) for l in [self.assembly_report_header, self.assembly_report_line1]]
            open_file.write('\n'.join(lines))

    def tearDown(self) -> None:
        shutil.rmtree(os.path.join(self.genome_folder))

    def test_get_assembly_report_rows(self):
        expected_lines = [
            {'# Sequence-Name': 'ANONYMOUS', 'Sequence-Role': 'assembled-molecule', 'Assigned-Molecule': 'na',
             'Assigned-Molecule-Location/Type': 'Chromosome', 'GenBank-Accn': 'BA000007.2', 'Relationship': '=',
             'RefSeq-Accn': 'NC_002695.1', 'Assembly-Unit': 'Primary Assembly', 'Sequence-Length': '5498450',
             'UCSC-style-name': 'na'},
            {'# Sequence-Name': 'pO157', 'Sequence-Role': 'assembled-molecule', 'Assigned-Molecule': 'pO157',
             'Assigned-Molecule-Location/Type': 'Plasmid', 'GenBank-Accn': 'AB011549.2', 'Relationship': '=',
             'RefSeq-Accn': 'NC_002128.1', 'Assembly-Unit': 'Primary Assembly', 'Sequence-Length': '92721',
             'UCSC-style-name': 'na'},
            {'# Sequence-Name': 'pOSAK1', 'Sequence-Role': 'assembled-molecule', 'Assigned-Molecule': 'pOSAK1',
             'Assigned-Molecule-Location/Type': 'Plasmid', 'GenBank-Accn': 'AB011548.2', 'Relationship': '=',
             'RefSeq-Accn': 'NC_002127.1', 'Assembly-Unit': 'Primary Assembly', 'Sequence-Length': '3306',
             'UCSC-style-name': 'na'},
        ]
        for i, line_dict in enumerate(self.assembly.get_assembly_report_rows()):
            self.assertEqual(line_dict, expected_lines[i])

    def test_download_assembly_report(self):
        self.assertFalse(os.path.isfile(self.assembly.assembly_report_path))
        self.assembly.download_assembly_report()
        self.assertTrue(os.path.isfile(self.assembly.assembly_report_path))

    def test_download_assembly_fasta(self):
        self.assertFalse(os.path.isfile(self.assembly.assembly_fasta_path))
        self.assembly.download_assembly_fasta()
        self.assertTrue(os.path.isfile(self.assembly.assembly_fasta_path))

    def test_construct_fasta_from_report(self):
        self.assertTrue(os.path.isfile(self.assembly_from_report.assembly_report_path))
        self.assembly_from_report.construct_fasta_from_report()
        self.assertTrue(os.path.isfile(self.assembly_from_report.assembly_fasta_path))
        self.assertEqual(
            NCBIAssembly.get_written_contigs(self.assembly_from_report.assembly_fasta_path),
            ['LODP01002389.1']
        )

    def test_download_or_construct(self):
        self.assertFalse(os.path.isfile(self.assembly.assembly_report_path))
        self.assertFalse(os.path.isfile(self.assembly.assembly_fasta_path))
        # Get the assembly from the FTP
        self.assembly.download_or_construct()
        self.assertTrue(os.path.isfile(self.assembly.assembly_report_path))
        self.assertTrue(os.path.isfile(self.assembly.assembly_fasta_path))

        self.assertEqual(
            NCBIAssembly.get_written_contigs(self.assembly.assembly_fasta_path),
            ['BA000007.2', 'AB011549.2', 'AB011548.2']
        )

        # Append to the assembly report and download the
        with open(self.assembly.assembly_report_path, 'a') as open_file:
            open_file.write('\t'.join(self.assembly_report_line1) + '\n')

        # Disable the object capability to access the FTP and delete the cached URL to show that only the new
        # contig is downloaded.
        self.assembly._ncbi_genome_folder_url_and_content = Mock()
        self.assembly.__dict__['assembly_report_url']
        self.assembly.__dict__['assembly_fasta_url']

        self.assembly.download_or_construct()
        self.assertEqual(
            NCBIAssembly.get_written_contigs(self.assembly.assembly_fasta_path),
            ['BA000007.2', 'AB011549.2', 'AB011548.2', 'LODP01002389.1']
        )
