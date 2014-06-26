__author__ = 'pvaut'
import math

# !!! WARNING: this code currently does not include wrapping around the Earth (i.e. longit 360 -> 0)

def CalcDist(pt1, pt2):
    R = 6371
    lat1 = math.radians(pt1['latit'])
    lat2 = math.radians(pt2['latit'])
    lon1 = math.radians(pt1['longit'])
    lon2 = math.radians(pt2['longit'])
    return R * math.sqrt((lat2-lat1)**2 + (math.cos((lat2+lat1)/2)*(lon2-lon1))**2)

def Aggregate(points, maxdist):
    print('================= Geo aggregation ====================================')
    print('Number of points: '+str(len(points)))
    print('Distance (km): '+str(maxdist))

    # For each point, find the number of other points within distance
    for pt in points:
        ct = 0
        for pt2 in points:
            if CalcDist(pt, pt2) <= maxdist:
                ct += 1
        ct -= 1
        pt['dist1count'] = ct

    clusters = []
    for pt in points:
        pt['cluster'] = None

    #Find point with maximum neighbors, and initiate cluster
    while True:
        maxct = 1
        maxpt = None
        for pt in points:
            if (pt['cluster'] is None) and (pt['dist1count'] >= maxct):
                maxct = pt['dist1count']
                maxpt = pt
        if maxpt is not None:
            cluster = {
                'longit': maxpt['longit'],
                'latit': maxpt['latit'],
                'members': []
            }
            for pt in points:
                if (pt['cluster'] is None) and (CalcDist(cluster, pt) <= maxdist):
                    pt['cluster'] = cluster
                    cluster['members'].append(pt)
            clusters.append(cluster)
            #print('ADDED CLUSTER: '+str(cluster))
        else:
            break

    print('CLUSTER INITIATION COMPLETED. Clusters: '+str(len(clusters)))
    for cluster in clusters:
        print('{longit},{latit}, MemberCount={membercount}'.format(
            longit=cluster['longit'],
            latit=cluster['latit'],
            membercount=len(cluster['members'])
        ))

    # Move cluster to center of gravity of points
    for cluster in clusters:
        cluster['longit'] = 0
        cluster['latit'] = 0
        cluster['membercount'] = 0
    for pt in points:
        cluster = pt['cluster']
        if cluster is not None:
            cluster['membercount'] += 1
            cluster['longit'] += pt['longit']
            cluster['latit'] += pt['latit']
    for cluster in clusters:
        if cluster['membercount'] > 0:
            cluster['longit'] /= cluster['membercount']
            cluster['latit'] /= cluster['membercount']

    # Assign points to closest cluster
    for pt in points:
        mindist = maxdist
        bestcluster = None
        for cluster in clusters:
            dist =CalcDist(cluster, pt)
            if dist <= mindist:
                mindist =dist
                bestcluster = cluster
        pt['cluster'] = bestcluster


    # Replace point coordinates by cluster coordinates
    for pt in points:
        cluster = pt['cluster']
        if cluster is not None:
            pt['longit'] = cluster['longit']
            pt['latit'] = cluster['latit']