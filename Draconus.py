import os

from app.draconus import Draconus
from app.tools.builder import Builder


from app.tools.draco_starter import DracoStarter


if __name__ == "__main__":
    opt = DracoStarter()
    opt = opt.output()
    builder = Builder(opt.get("EXTRA_CONFIG"))
    draco = Draconus(builder, opt)
    draco.Start()



# if __name__ == "__main__":
#     options = Starter(sys.argv)
#     builder = Builder(options.args.get("extra_config", None))
#     draco = Draconus(builder, **options.args)
#     draco.Start()
#     # input()
#     # draco.Exit()
    