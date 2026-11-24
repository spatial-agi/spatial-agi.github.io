from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/"source/pipeline"))
from extract_figures81_825 import make_figure
if __name__=="__main__": make_figure(3)
