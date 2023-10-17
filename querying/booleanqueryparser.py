from . import AndQuery, OrQuery, QueryComponent, TermLiteral, PhraseLiteral, NotQuery

class BooleanQueryParser:
    class _StringBounds:
        def __init__(self, start : int, length : int):
            self.start = start
            self.length = length

    class _Literal:
        def __init__(self, bounds : 'BooleanQueryParser._StringBounds', literal_component : QueryComponent):
            self.bounds = bounds
            self.literal_component = literal_component

    @staticmethod
    def _find_next_subquery(query : str, start_index : int) -> _StringBounds:
        length_out = 0

        # Find the start of the next subquery by skipping spaces and + signs.
        test = query[start_index]
        while test == ' ' or test == '+':
            start_index += 1
            test = query[start_index]

        # Find the end of the next subquery.
        next_plus = query.find("+", start_index + 1)
        if next_plus < 0:
            # If there is no other + sign, then this is the final subquery in the
			# query string.
            length_out = len(query) - start_index
        else:
            # If there is another + sign, then the length of this subquery goes up
			# to the next + sign.
		
			# Move next_plus backwards until finding a non-space non-plus character.
            test = query[next_plus]
            while test == ' ' or test == '+':
                next_plus -= 1
                test = query[next_plus]

            length_out = 1 + next_plus - start_index

        # startIndex and lengthOut give the bounds of the subquery.
        return BooleanQueryParser._StringBounds(start_index, length_out) 
			
    @staticmethod
    def _find_next_literal(subquery : str, start_index : int) -> 'BooleanQueryParser._Literal':
        """
        Locates and returns the next literal from the given subquery string.
        """
        sub_length = len(subquery)
        length_out = 0

        # Skip past white space.
        while subquery[start_index] == ' ':
            start_index += 1

        # Check if this is a NOT component
        if subquery[start_index] == '-':
            literal = BooleanQueryParser._find_next_literal(subquery, start_index + 1)
            return BooleanQueryParser._Literal(
                BooleanQueryParser._StringBounds(start_index, literal.bounds.length + 1),
                NotQuery(literal.literal_component)
            )

        # Check if this is a phrase literal
        if subquery[start_index] == '"':
            next_quote = subquery.find('"', start_index + 1)
            if next_quote >= 0:
                phrase_contents = subquery[start_index+1:next_quote]
                length_out = next_quote - start_index+1
                # Use parse_query to parse the phrase contents. It will return an AndQuery containing a bunch of 
                # literals from the phrase.
                phrase_literals = BooleanQueryParser.parse_query(phrase_contents)
                return BooleanQueryParser._Literal(
                    BooleanQueryParser._StringBounds(start_index, length_out),
                    PhraseLiteral(phrase_literals.components)
                )

            else:
                pass
                # This is a malformed phrase missing a second quotation mark. 
                # Fall through and continue as a regular literal.



        # Locate the next space to find the end of this literal.
        next_space = subquery.find(' ', start_index)
        if next_space < 0:
            length_out = sub_length - start_index
        else:
            length_out = next_space - start_index
        
        # This is a term literal containing a single term.
        return BooleanQueryParser._Literal(
            BooleanQueryParser._StringBounds(start_index, length_out),
            TermLiteral(subquery[start_index:start_index + length_out])
        )

        # TODO:
		# Instead of assuming that we only have single-term literals, modify this method so it will create a PhraseLiteral
		# object if the first non-space character you find is a double-quote ("). In this case, the literal is not ended
		# by the next space character, but by the next double-quote character.

    @staticmethod
    def parse_query(query : str) -> QueryComponent:
        all_subqueries = []
        start = 0

        while True:
            # Identify the next subquery: a portion of the query up to the next + sign.
            next_subquery = BooleanQueryParser._find_next_subquery(query, start)
            # Extract the identified subquery into its own string.
            subquery = query[next_subquery.start:next_subquery.start + next_subquery.length]
            sub_start = 0

            # Store all the individual components of this subquery.
            subquery_literals = []

            while True:
                # Extract the next literal from the subquery.
                lit = BooleanQueryParser._find_next_literal(subquery, sub_start)

                # Add the literal component to the conjunctive list.
                subquery_literals.append(lit.literal_component)

                # Set the next index to start searching for a literal.
                sub_start = lit.bounds.start + lit.bounds.length
                if sub_start >= len(subquery):
                    break

            # After processing all literals, we are left with a conjunctive list
			# of query components, and must fold that list into the final disjunctive list
			# of components.
			
			# If there was only one literal in the subquery, we don't need to AND it with anything --
			# its component can go straight into the list.
            if len(subquery_literals) == 1:
                all_subqueries.append(subquery_literals[0])
            else:
                # With more than one literal, we must wrap them in an AndQuery component.
                all_subqueries.append(AndQuery(subquery_literals))
          
            start = next_subquery.start + next_subquery.length
            if start >= len(query):
                break
        
        # After processing all subqueries, we either have a single component or multiple components
		# that must be combined with an OrQuery.
        if len(all_subqueries) == 1:
            return all_subqueries[0]
        elif len(all_subqueries) > 1:
            return OrQuery(all_subqueries)
        else:
            return None
