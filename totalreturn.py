import datetime

import divhistory as div
import stkhistory as stk



# requirements: stkhistory & divhistory
# calculates total return based on dividends collected over time & capital appreciation
# needs to include DRIP as well as commissions


def calc_total_return(symbol,
                      shares=100,
                      end_date=datetime.datetime.today(),
                      beg_date=(datetime.datetime.today()-datetime.timedelta(days=365)), 
                      display_summary=True,
                      return_table=False):
    
    if type(end_date) == str:
        end_date = datetime.datetime.strptime(end_date, "%m-%d-%Y")
    if type(beg_date) == str:
        end_date = datetime.datetime.strptime(beg_date, "%m-%d-%Y")
        
    # get respective series for requested timeframe
    div_series = div.get_dividend_history(symbol)[end_date:beg_date]
    div_series['DivAmt'] = div_series['DivAmt'].str.replace('$','').astype(float)
    stk_series = stk.get_price_history(symbol)['Close'][end_date:beg_date]
    
    all_data = pd.concat([div_series, stk_series], axis=1).fillna(0)
    all_data['Cap Appr (from beg)'] = (all_data['Close'] - all_data['Close'].iloc[0])
    all_data['Div Ret (from beg)'] = all_data['DivAmt'].cumsum()
    
    beg_price = all_data.iloc[0]['Close']
    end_price = all_data.iloc[-1]['Close']
    end_div_return_pshare = all_data.iloc[-1]['Div Ret (from beg)']
    end_cap_appr_pshare = all_data.iloc[-1]['Cap Appr (from beg)'] 
    
    end_div_return = end_div_return_pshare * shares
    end_cap_appr = end_cap_appr_pshare * shares
    total_return = end_div_return + end_cap_appr

    pct_div_ret = "{0:.3f} %".format((end_div_return_pshare/beg_price)*100)
    pct_cap_ret = "{0:.3f} %".format((end_cap_appr_pshare/beg_price)*100)
    pct_ttl_ret = "{0:.3f} %".format(total_return/(shares*beg_price)*100)
    
    num_divs = len(all_data[all_data['DivAmt'] > 0])
    inv_duration = (end_date - beg_date).days
    
    if display_summary:
        print('Beg Price: {0}'.format(beg_price))
        print('End Price: {0}'.format(end_price))
        print('Shares: {0}'.format(shares))
        print('Number of  div paymnts: {0}'.format(num_divs))
        print('Duration: {0} days'.format(inv_duration))
        print('Gross Dividend Ret: ${0:.2f}'.format(end_div_return))
        print('               (pct): {0}'.format(pct_div_ret))    
        print('Gross Capital Appr: ${0:.2f}'.format(end_cap_appr))
        print('               (pct): {0}'.format(pct_cap_ret))
        print('Total Return: ${0:.2f}'.format(total_return))
        print('          (pct): {0}'.format(pct_ttl_ret))
        print('-- -- --')
        
    if return_table:
        return all_data
        
    data_dict = {'BegPrice': beg_price,
                 'EndPrice': end_price,
                 'Shares': shares,
                 'Num Divs': num_divs,
                 'Duration': inv_duration,
                 'GrossDivRet': end_div_return,
                 'PctDivRet': pct_div_ret,
                 'GrossCapApr': end_cap_appr,
                 'PctCapRet': pct_cap_ret,
                 'GrossTtlRet': total_return,
                 'PctTtlRet': pct_ttl_ret,
                 'BegDate': beg_date.date(),
                 'EndDate': end_date.date(),
                 'Symbol': symbol}
        
    return data_dict