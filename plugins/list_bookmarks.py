from yapsy.IPlugin import IPlugin
from operator import itemgetter

class PluginListBookmarks(IPlugin):

    def execute(self, api):

        api.print('----------------------------------')

        bookmarks = api.get_bookmarks()
        if not bookmarks:
            api.print('No bookmarks found.')
            return

        for b in bookmarks:
            row = '{:<8}'.format(b.startrow)
            api.print(row + '{:<20}'.format(b.disasm) + '; %s' % b.comment)

        api.print('')

        addresses = {}
        for b in bookmarks:
            if b.addr in addresses:
                addresses[b.addr] += 1
            else:
                addresses[b.addr] = 1
        addresses = sorted(addresses.items(), key=itemgetter(1), reverse=True)

        api.print('Duplicate bookmarks:')
        api.print('Address  | count |  start row')
        for address, count in addresses:  # [:15]
            b_rows = []
            for b in bookmarks:
                if address == b.addr:
                    b_rows.append(b.startrow)
            b_rows_str = ' '.join(map(str, b_rows))
            api.print('%s |  %d    | %s' % (address, count, b_rows_str))

        api.print('')

        api.print('%d bookmarks total.' % len(bookmarks))
        api.print('%d unique bookmarks.' % len(addresses))

        lengths = []
        for b in bookmarks:
            lengths.append(b.endrow - b.startrow + 1)
        avg_len = sum(lengths) / len(bookmarks)
        shortest = min(lengths)
        longtest = max(lengths)
        api.print('Average length of bookmarks: %d' % avg_len)
        api.print('Longest: %d  Shortest: %d' % (longtest, shortest))
