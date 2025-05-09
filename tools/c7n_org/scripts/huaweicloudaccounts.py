# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import click
import jmespath
from huaweicloudsdkorganizations.v1 import ListAccountsRequest

from c7n.utils import yaml_dump
from c7n_huaweicloud.client import Session


def get_next_page_params(response=None):
    if not response:
        return None
    page_info = jmespath.search("page_info", response)
    if not page_info:
        return None
    return page_info.get("next_marker")


@click.command()
@click.option(
    '-f', '--output',
    type=click.File('w'), default='accounts.yml',
    help="File to store the generated config. default: ./accounts.yml")
@click.option(
    '-n', '--agency_name',
    type=str, default='custodian_agency',
    help="trust agency name. default:custodian_agency")
@click.option(
    '-d', '--duration_seconds',
    default=900, type=int,
    help="assume session duration second. default:900")
@click.option(
'-r', '--regions',
    multiple=True, type=str, default=('cn-north-4',),
    help="huaweicloud region for executing policy. default:cn-north-4")
def main(output, agency_name, duration_seconds, regions):
    """
    Generate a c7n-org huawei cloud accounts config file
    """
    options = {"region": 'cn-north-4'}
    accounts = []
    marker = None
    session = Session(options)
    client = session.client("org-account")
    while True:
        request = ListAccountsRequest(limit=1000, marker=marker)
        response = client.list_accounts(request)
        marker = get_next_page_params(response)
        for account in response.accounts:
            accounts.append(account)
        if not marker:
            break
    results = []
    for account in accounts:
        acc_info = {
            'name': account.name,
            'domain_id': account.id,
            'agency_urn': f"iam::{account.id}:agency:{agency_name}",
            'duration_seconds': duration_seconds,
            'regions': regions
        }
        results.append(acc_info)

    print(yaml_dump({'domains': results}), file=output)


if __name__ == '__main__':
    main()
