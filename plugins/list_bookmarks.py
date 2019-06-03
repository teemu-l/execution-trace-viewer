from yapsy.IPlugin import IPlugin
from operator import itemgetter

class PluginListBookmarks(IPlugin):

    def execute(self, main_window, trace_data, selected_row_ids):

        main_window.print('----------------------------------')

        bookmarks = trace_data.get_bookmarks()
        if not bookmarks:
            main_window.print('No bookmarks found.')
            return

        for b in bookmarks:
            row = '{:<8}'.format(b.startrow)
            main_window.print(row + '{:<20}'.format(b.disasm) + '; %s' % b.comment)

        main_window.print('')

        addresses = {}
        for b in bookmarks:
            if b.addr in addresses:
                addresses[b.addr] += 1
            else:
                addresses[b.addr] = 1
        addresses = sorted(addresses.items(), key=itemgetter(1), reverse=True)

        main_window.print('Duplicate bookmarks:')
        main_window.print('Address  | count |  start row')
        for address, count in addresses:  # [:15]
            b_rows = []
            for b in bookmarks:
                if address == b.addr:
                    b_rows.append(b.startrow)
            b_rows_str = ' '.join(map(str, b_rows))
            main_window.print('%s |  %d    | %s' % (address, count, b_rows_str))

        main_window.print('')

        main_window.print('%d bookmarks total.' % len(bookmarks))
        main_window.print('%d unique bookmarks.' % len(addresses))

        lengths = []
        for b in bookmarks:
            lengths.append(b.endrow - b.startrow + 1)
        avg_len = sum(lengths) / len(bookmarks)
        shortest = min(lengths)
        longtest = max(lengths)
        main_window.print('Average length of bookmarks: %d' % avg_len)
        main_window.print('Longest: %d  Shortest: %d' % (longtest, shortest))
