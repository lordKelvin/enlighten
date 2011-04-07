def lightUp(player, outline):
    visible = []
    u = player
    for i, c in enumerate(outline):
        c0 = outline[i - 1]
        c2 = outline[(i + 1) % len(outline)]
        rib0 = (c0[0] - c[0]) * u[1] - (c0[1] - c[1]) * u[0] > c0[0] * c[1] - c0[1] * c[0]
        rib1 = (c[0] - c2[0]) * u[1] - (c[1] - c2[1]) * u[0] > c[0] * c2[1] - c[1] * c2[0]
        fail = False
        kmin = 0
        for j, n2 in enumerate(outline):
            n1 = outline[j - 1]
            C = (c[0] - u[0], c[1] - u[1])
            B = (n2[0] - n1[0], n2[1] - n1[1])
            X = (u[0] - n1[0], u[1] - n1[1])
            div = C[0] * B[1] - C[1] * B[0]
            if div:
                k = (B[0] * X[1] - B[1] * X[0]) / float(div)
                m = (C[0] * X[1] - C[1] * X[0]) / float(div)
                if k > 0 and m == 1:
                    n3 = outline[(j + 1) % len(outline)]
                    one = (n1[0] - n2[0]) * u[1] - (n1[1] - n2[1]) * u[0] > n1[0] * n2[1] - n1[1] * n2[0]
                    two = (n2[0] - n3[0]) * u[1] - (n2[1] - n3[1]) * u[0] > n2[0] * n3[1] - n2[1] * n3[0]
                    if one == two:
                        if k < 1:
                            fail = True
                            break
                        else:
                            if kmin == 0 or kmin > k:
                                kmin = k

                if k > 0 and m > 0 and m < 1:
                    if k < 1:
                        fail = True
                        break
                    else:
                        if kmin == 0 or kmin > k:
                            kmin = k
        if not fail:
            extra = ()
            if rib0 != rib1:
                extra = (int(u[0] + C[0] * kmin + .5), int(u[1] + C[1] * kmin + .5))
                if rib0:
                    visible.append(extra)

            visible.append(c)

            if not rib0 and rib1:
                visible.append(extra)
    return visible

