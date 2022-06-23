"""Unused atm, Will be used for the command line generator"""
import sys, os

LOCAL = os.path.dirname(os.path.realpath(__file__))

# if filepath does not start with C: it will use the local path

class Main():
    def __init__(self):
        self.output = os.path.join(LOCAL, 'generated')
        self.jar = None
        self.client = False
        self.server = False

        self.index=None
        self.objects=None
    
    def path(self, path:str):
        return os.path.join(LOCAL, path)

    def parse_args(self, *args):
        i=0
        for arg in args:
            # print(arg)
            if i!=0:
                if arg=='--help':
                    self.help()
                elif arg=='--output':
                    try: self.output = self.path(args[i+1])
                    except IndexError: self.help()
                elif arg=='--jar':
                    try:self.jar = self.path(args[i+1])
                    except IndexError: self.help()

                elif arg=='--client': self.client=True
                elif arg=='--server': self.server=True

                elif arg=='--objects':
                    try:self.objects = self.path(args[i+1])
                    except IndexError: self.help()
                    
                elif arg=='--index':
                    try:self.index = self.path(args[i+1])
                    except IndexError: self.help()

            i+=1
        
        self.run()

    def help(self):
        menu = """Option             Description
------             -----------
--help             Show the help menu
--output <String>  Output folder (default: generated)
--jar <String>     Jar file for jar extractor
--objects <String> Objects folder for object mapper
--index <String>   Index file for object mapper
--client           Include client generators
--server           Include server generators
"""
        print(menu)

    def run(self):
        if self.jar!=None:
            print('**JAR EXTRACTOR**')
            print('OUTPUT',self.output)
            print('JAR',self.jar)
            print('CLIENT',self.client)
            print('SERVER',self.server)
        if self.index!=None and self.objects:
            print('**OBJECT MAPPER**')
            print('OUTPUT',self.output)
            print('INDEX',self.index)
            print('OBJECTS',self.objects)

if __name__== '__main__':
    asd = Main()
    asd.parse_args(*sys.argv)


    # Make a command handler class
    # types: subcommand (like enum), str, int, number, float
    # pip <install: subcommand> <(module): enum> <vars>
    # -VAR will see it as `-V`
    # --VAR will see it as `--VAR` uses re.search so it will best match that func