"""
ReportWithLevels
__author__ = 'Margery Harrison'
__license__ = "Public Domain"
__version__ = "1.1"

To use this:
1) create an object of this class
2) if you don't want to report to stdout, then call open_outfile()
   --> pass to open_outfile the path to the output file
3) Call write_line() to write header lines or any other explanations
4) For each set of messages and sums,
    call print_level(level,message,sum)
    level indicates amount to indent
    message is the part that explains the sum
    sum is right justified as a numeric field.
"""

import sys

class ReportWithLevels():

    def __init__(self):
        """
        Sets the default values for the class
        """
        self.fdout=sys.stdout  #default - writes report to stdout
        self.number_width=10
        self.level_indent=2
        self.total_width=30
        self.debug = False
        self.min_level = 1
        self.max_level = 4

        #levels before which to print a newline
        self.newline_before = [1]

    # open the input path as file to write to
    def open_outfile(self,path):
        try:
            self.fdout = open(path,'w')
        except IOError:
            msg="{0:s} Can't open and write to {1:s}".format(self.__class__.__name__,path)
            sys.stderr.write(msg)

    # print debug statement if debugging turned on
    def debug_print(self,message):
        if self.debug:
            print(message)


    def write_indent(self,message,level):
        if level > 0:
            indent=' ' * (level * self.level_indent)
        else:
            indent='  '

        self.fdout.write('{0:s}{1:s}'.format(indent,message))

    # Write a line out to the output file with newline at end
    # adding indentation level for beginning
    def write_line(self,message,lev=0):
        if lev==0:
            self.fdout.write(message + '\n')
        else:
            self.write_indent(message,lev)
            self.fdout.write('\n')

    # for printing msg,sum pairs when report is getting dense
    def print_on_same_line(self,message,total,level=0):
        """

        :param message: string to go with the total sum
        :param total:   total sum to go with the message
        :param level: OPTIONAL - begins message at level-appropriate indendation
        """
        #create a string of spaces called 'indent'
        if level > 0:
            indent=' ' * (level * self.level_indent)
        else:
            indent='  '
        self.fdout.write('{0:s}{1:s}: {2:d}  '.format(indent,message,total))

    # Print message and total with indentation set by input level
    # default sort of print-message
    def print_on_new_line(self, level, message, total):
        """
        :type level: int indicating indentation level
        :type message: str that goes with int total
        :type total:  int sum that goes with message
        """
        lev=int(level)
        #skip a space before level 1 statements
        if lev in self.newline_before:
            self.write_line('')

        #s1 and s2 are number of spaces for formatting
        s1 = lev * self.level_indent
        s2 = self.total_width - s1

        #initialize fstr to the correct number of spaces
        fstr='{{0:{0:d}s}} {{1:{1:d}s}}'.format(s1,s2)

        # Number format string is right justified within number_width
        number_format='{{2:-{0:d}d}}'.format(self.number_width)
        fstr+=number_format
        self.debug_print('level {0:d} format str= {1:s}'.format(lev,fstr))

        self.write_line(fstr.format(' ', message, int(total)))


    # Print message and total with indentation set by input level
    # dispatches printing to either print_on_same_line or print_on_new_line
    def print_level(self, level, message, total):
        """
        :type level: int
        :type message: str
        :type total:  int
        """
        lev=int(level)
        #assert lev >= self.min_level and lev <= self.max_level,\
        #    "input level not within current limits"
        if lev > self.max_level:
            self.print_on_same_line(message,total)
        else:
            self.print_on_new_line(level,message,total)

if __name__ == '__main__':
    print "Testing ReportWithLevels.printLevel()"
    pl=ReportWithLevels()
    pl.open_outfile("testout.txt")
    pl.write_line("This is my report")
    pl.number_width=12
    tot=7
    for level in [1,2,3,2,2,3,4,3,1]:  #range(1,4):
        msg='level {0:d} msg'.format(level)
        tot=tot * 12
        pl.print_level(level,msg,tot)
