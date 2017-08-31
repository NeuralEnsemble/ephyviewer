import ephyviewer

import numpy as np
import pandas as pd



def test_dataframe_view():
    
    
    df = pd.DataFrame()
    df['time'] = np.arange(0,10,.25)
    df['factorA'] = ['a', 'b', 'c', 'd']*10
    df['factorB'] = [10,20]*20
    df['quality'] = ['good', 'bad']*20
    
    
    app = ephyviewer.mkQApp()
    view = ephyviewer.DataFrameView(source=df, name='table')
    
    win = ephyviewer.MainViewer(debug=True)
    win.add_view(view)
    win.show()
    
    app.exec_()

    
    
if __name__=='__main__':
    test_dataframe_view()
