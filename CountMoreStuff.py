import csv
import collections
import ReportWithLevels


class CountMoreStuff:
    def __init__(self):
        """
        initializes class variables to nothing
        """
        #self.split_char = '_'
        self.my_reader = None
        self.my_counter = None
        self.format_dict = None

        # this is set to a parameter to countLevels()
        self.ordered_headers = None

        # create a dictionary of sets of values for each column indexed by its header
        self.value_sets=dict()

        # array of tuples indexed by len(tuple) from 2 to total_levels
        self.combo_sets=dict()

        self.total_levels=0 #convenience, = len(self.ordered_headers)

        self.max_per_line = 4


    def dict_message(self,msg):
        #if there's no format_dict then just return input
        if not self.format_dict:
            return msg
        if self.format_dict.has_key(msg):
            return self.format_dict[msg]
        else:
            return msg

    def dict_message_tuple(self,msg_tuple):
        """

        :param msg_tuple: tuple of column values to be translated into words
        :return: returns concatenated string
        """
        to_return = ""
        for m in msg_tuple:
            if self.format_dict.has_key(m):
                r=self.format_dict[m]
            else:
                r=m
            #concatenate the value from the dict (or not) to end
            to_return = '{0:s} {1:s}'.format(to_return,r)
        return(to_return)

    def count_levels(self, path, headers):
        """
        Takes the names of the important fields to count
        :param headers:   list of column titles to count

        Expects the CSV to have the header fields on the top line.
        Will return Counter with counts of
         number of records with header columns set to different values
        """
        c = collections.Counter()

        #Save the order in which the counter combinations created
        self.ordered_headers=headers
        self.total_levels=len(headers)

        #build an array of combination tuple possible values
        # e.g. self.combo_sets[2]=(triangle,red),(triangle,green),(square,red)...
        # and self.combo_sets[3]=(triangle,red,fuzzy),(triangle,red,smooth)...
        for level in range(2,self.total_levels+1):
            self.combo_sets[level]=set([])

        with open(path) as csv_file:
            self.my_reader = csv.DictReader(csv_file)

            # validate that input fields match those read from 1st line of CSV:
            for head in headers:
                assert head in self.my_reader.fieldnames, "{0:s} not in CSV fields"
                # save the header name and create an empty set to hold its values
                self.value_sets[head]=set([])

            # now loop through CSV file
            for row in self.my_reader:
                combo = None
                #print row <-fine for debug, but not with BIG file
                # start with level = 1
                for level, head in enumerate(headers,1):
                    # thing is the value at that column
                    thing = row[head]
                    # add it to the set of possible values for that column
                    self.value_sets[head].add(thing)
                    # increment the count of that value for that column
                    c[thing] += 1

                    #build the combo string for counting combinations of values
                    if level == 1:
                        combo = (thing,) #start a tuple
                    else:
                        combo += (thing,)
                        #combo = '{0:s}{1:s}{2:s}'.format(combo,self.split_char,thing)
                        c[combo] += 1

                        self.combo_sets[level].add(combo)

            # set the class variable so we can have this counter built-in
            self.my_counter = c
            return c


    #Use the self.ordered_headers to output a set of totals
    # start simple
    def defaultReport1(self,rfd):
        # copy class var to list you can pop
        heads = self.ordered_headers
        #for head in self.ordered_headers:
        # while the list is not empty
        while heads:
            head = heads.pop()
            vset=self.value_sets[head]
            print head
            print vset
            rfd.writeLine(head)
            for item in vset:
                level = 1
                total=self.my_counter[item]
                print item, total
                rfd.print_level(level,self.dict_message(item),total)

                #keep counting lower levels if upper not zero sum
                while level < self.total_levels and total > 0:
                    total=0
                    level +=1
                    #print sublevels
                    for combo in self.combo_sets[level]:
                        if item in combo:
                            subtotal=self.my_counter[combo]
                            total+=subtotal
                            rfd.print_level(level,self.dict_message_tuple(combo),subtotal)

    #Here we will use recursion..
    def print_sub_levels(self, rfd, combo_start):
        """
        Find other combos that share the start of the input combo
        Print indented messages and sums
        :param combo: tuple for current report lines
        :param level: from 2 to total levels
        """
        #if combo_start=(a,b) then looking at level 3 combos, (a,b,c)...
        level = len(combo_start)

        head = self.ordered_headers[level]
        #print "At sublevel ", level, head
        level += 1  #looking at combos one level beyond header..
        #print "For combo_set"
        #print self.combo_sets[level]

        # before you start looping through the possible values for this level,
        # check if they will all end up on one line.
        if level > rfd.max_level:
            rfd.write_line("")
            rfd.write_line(head,level)
            rfd.write_indent(' ',level)
            tab_count=0
            for item in self.value_sets[head]:
                combo=combo_start + (item,)
                if combo in self.combo_sets[level]:
                    total=self.my_counter[combo]
                    # if already printed max on this line, start a new line
                    if tab_count == self.max_per_line:
                        rfd.write_line(' ')
                        rfd.write_indent(' ',level)
                        tab_count=0
                    rfd.print_on_same_line(self.dict_message(item),total)
                    tab_count += 1
                    if total > 0 and level < self.total_levels:
                        self.print_sub_levels(rfd,combo)
                        tab_count = self.max_per_line

            rfd.write_line("")

        else:
            for item in self.value_sets[head]:
                combo=combo_start + (item,)
                if combo in self.combo_sets[level]:
                    total=self.my_counter[combo]
                    rfd.print_level(level,self.dict_message(item),total)
                    if total > 0 and level < self.total_levels:
                        self.print_sub_levels(rfd,combo)

    #report_file='crime_report_5.txt'
    # improve order of output to go under combos
    # Print first 2 levels,
    #  pass tuple to other thing below
    def default_report(self,rfd):

        head1=self.ordered_headers[0]
        vset1=self.value_sets[head1]

        head2=self.ordered_headers[1]
        vset2=self.value_sets[head2]

        #rfd.writeLine(head1) used for earlier versions, removing
        for item1 in vset1:
            total=self.my_counter[item1]
            #print item1, total  #debug
            rfd.print_level(1,self.dict_message(item1),total)
            if total > 0:
                for item2 in vset2:
                    combo = (item1,item2)
                    # combo is not necessarily in recorded set of combinations
                    if combo not in self.combo_sets[2]:
                        print ("can't find {0:s}".format(str(combo)))
                        total=0
                    else:
                        total=self.my_counter[combo]
                    rfd.print_level(2,self.dict_message_tuple(combo),total)
                    if total > 0:
                        self.print_sub_levels(rfd,combo)

